GitHub Actions 整合
===================

Reviewer 內附一份可直接用的 workflow：\ ``.github/workflows/prthinker.yml``\ 。
它在 ``pull_request`` ``opened`` / ``synchronize`` / ``reopened`` 時觸發，
透過同一個 PR 回貼 review。

Workflow 結構
-------------

Workflow 拆成三個 job，避免某個慢檔案或大 PR 卡死整段 review：

1. **enumerate**（12 分鐘）— 列出 PR 改動的 files，依
   ``PRTHINKER_EXCLUDE_GLOBS`` 過濾 noise paths，把剩下的清單以 JSON
   output 傳給下一個 job 的 matrix，並貼出 Copilot 式 pre-review PR
   摘要（見下方「審查前 PR 摘要」一節）。
2. **review**（matrix，每 shard 60 分鐘，``max-parallel: 1``）— 每個
   matrix 跑一個 file，傳 ``PRTHINKER_TARGET_FILE`` 給 CLI，把 partial
   ``ReviewResult`` 透過 ``PRTHINKER_OUTPUT_JSON`` 寫到
   ``$RUNNER_TEMP/partial.json``\ ，再以 ``partial-<job-index>`` 為名
   上傳成 artifact。Matrix runner **不**直接 post 到 GitHub、也不開
   gate — 那些事交給 aggregate。
3. **aggregate**（15 分鐘，``if: always()``）— 下載所有 ``partial-*``
   artifact，跑 ``prthinker aggregate`` 把 ``inline_findings`` +
   ``per_file`` + ``step_outputs`` 合一，post **一個** summary 留言、
   **一個** inline review，並把合併前 gate 開 + 關各做一次。

``max-parallel: 1`` 是故意的：推論 backend 在單一 GPU 上必然序列處理，
並行 matrix runner 只會在 ``/review/submit`` 排隊浪費 CI 分鐘。Matrix
的真正好處是 **per-file 隔離**：每個 file 各自 60 分鐘 budget，單一
慢檔案不會把其它 file 一併拖死。

為何用 job-pattern endpoint 而非同步 ``/review``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Remote runner 打 ``/review/submit`` 後每五秒輪詢
``/review/result/{id}``\ （見 :doc:`../reference/http-api`）。每次來回都
在一秒內完成，落在 Cloudflare 免費 / Pro / Business 方案的 100 秒 idle
timeout 內。同步 ``/review`` POST 會被 30B MoE 卡到 proxy 100 秒前直接
回 504。

取消與閒置 GPU 防護
~~~~~~~~~~~~~~~~~~~

Workflow 被取消時（``concurrency: cancel-in-progress`` 因新 push 觸發、
手動 cancel、runner crash）matrix runner 之 try/finally 會 post
``POST /review/cancel/{job_id}`` 通知 server。Backend 於下一個 step
邊界或下一個 decoded token（透過 ``StoppingCriteria``）中斷
``model.generate``。Server 另常駐 idle sweeper：任何 running job 若
180 秒未被 poll，自動 set ``cancel_event``，涵蓋 SIGKILL / 網路中斷等
try/finally 來不及執行之情境，避免 backend 持續耗用 GPU 跑沒人讀的
review。

審查前 PR 摘要
~~~~~~~~~~~~~~~~~~~~~~~

在 matrix 開始前，``enumerate`` job 會跑 ``prthinker pr-summary`` 貼出
Copilot 式 PR 概覽。它讀取 PR 標題、描述與 commit 訊息並對照 diff，以
專屬 marker ``<!-- prthinker:pr-summary -->`` upsert 一則獨立留言──與
review summary 分開、且更早貼出──含 ``### Overview``\ 、\ ``### Key
changes``\ 、\ ``### Areas to review``\ 、\ ``### Notes`` 等區段，核對
作者所寫與 diff 所做是否一致。指令見 :doc:`../reference/cli`\ 。

把呼叫放在 ``enumerate`` 使其早於逐檔審查，故其單次短 generate 於共享
GPU 上與審查維持序列。此步驟為 best-effort：health 探測與 generate 皆
會重試以越過短暫冷啟動之通道；持續失敗則 exit 0 並 log warning，永不
阻擋 matrix。與下方 aggregate 階段之 *Overall Summary* 不同──後者摘要
review 之發現，本節摘要變更本身。

PR-wide overall summary
~~~~~~~~~~~~~~~~~~~~~~~

Aggregate 合併所有 shard 的 partial 後，會以 job-pattern
``POST /ask/submit`` 對 backend 發起一次合成：input 為各 file 之
``total_summary``，要求模型寫一段 3-5 句之 PR-wide 總結。結果寫入
``merged.step_outputs["total_summary"]`` 並由 formatter 渲染為
``### Overall Summary``\ ，置於 PR 留言頂部、per-file ``<details>``
區塊之前。Best-effort：backend 不通 / 超時 / 任何 httpx 例外都 log
warning 並 fallback 為僅顯示 per-file blocks。

Summary comment / inline review / check run 之 dedup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

對同一 head SHA 重複 run workflow（手動 *Re-run all jobs*、
``cancel-in-progress`` 後新 push、CI retry）原本會於 PR 上累積多份
prthinker 產物。每次 post 前皆會清理同 SHA 之舊產物：

* **Summary comment** — 以 HTML marker ``<!-- prthinker:summary -->``
  upsert，永遠 PATCH 同一條 comment。
* **Inline review** — body 嵌入隱藏 marker
  ``<!-- prthinker:inline -->``\ 。post 新 review 前先列出所有
  marker-tagged review，並 DELETE 其底下每一條 review comment（GitHub
  不允許 dismiss COMMENT-state review，故 wrapper 留為 timeline stub
  但 diff 上不再顯示重複註解）。Cleanup 失敗只 log warning，不擋新
  review 提交。
* **Check run** — open gate 前先列出 head SHA 上所有同名
  ``prthinker`` check，逐一 PATCH 為 ``status=completed`` /
  ``conclusion=neutral`` 並附 *superseded* 標題；UI 會自動將 superseded
  之 check 折疊於 live 之 check 下方。

Concurrency 與 GPU 序列化
-------------------------

workflow 以 PR 為單位分組 concurrency 並取消進行中：

.. code-block:: yaml

   concurrency:
     group: prthinker-pr-${{ github.event.pull_request.number }}
     cancel-in-progress: true

故新 commit 會取代該 PR\ *自己*\ 仍在跑的 run──過時的審查被丟棄而非
跑完。不同 PR 不受影響：於 workflow 層級並行。

跨 PR 之 GPU 安全改由\ **伺服器端**\ 保證，而非 CI concurrency group。
推論伺服器上每次 ``model.generate`` 都在一道 process 級全域鎖下執行，
兩個 PR 同時審查時於 GPU 上排隊，而非跑兩個 forward pass 把顯卡 OOM。
正因此一解耦，per-PR 之 ``cancel-in-progress`` 才安全：CI 層不再需要序
列化 GPU。

必要 secrets
------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Secret
     - 用途
   * - ``PRTHINKER_BACKEND_URL``
     - 你自架的推論伺服器基底 URL
       （例如 ``https://gpu-host.internal:9000``\ ）。
   * - ``PRTHINKER_BACKEND_API_KEY``
     - 可選的 bearer token，會以 ``Authorization: Bearer ...`` 發送。

在 **Settings → Secrets and variables → Actions** 設定。

必要權限
--------

Workflow 宣告：

.. code-block:: yaml

   permissions:
     contents: read         # checkout
     pull-requests: write   # upsert 總結留言、提交 inline review
     checks: write          # 開啟與結算合併前的 Check Run gate
     actions: read          # 抓 CI 失敗 job 的 log

若你 fork 這份 workflow，請保留同樣的權限，不然功能會被默默跳過。

可調整的環境變數
----------------

Workflow 把最常用的 flag 都暴露成環境變數，這樣不用改 Python 也能改行為：

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - 變數
     - 預設
     - 效果
   * - ``PRTHINKER_BACKEND``
     - ``remote``
     - 設成 ``local`` 改在 runner 上載入 Qwen（需要 self-hosted GPU runner）。
   * - ``PRTHINKER_USE_REMOTE_PIPELINE``
     - ``true``
     - 用 ``/review`` 單回合呼叫，而不是每個 step 都打一次 ``/ask``\ 。
   * - ``PRTHINKER_PER_FILE``
     - ``true``
     - 逐檔執行 pipeline。
   * - ``PRTHINKER_INLINE_REVIEW``
     - ``true``
     - 產出 inline ``suggestion`` 區塊。
   * - ``PRTHINKER_MAX_FINDINGS_PER_FILE``
     - ``10``
     - 每個檔案最多保留幾筆 finding。
   * - ``PRTHINKER_RAG_ENABLED``
     - ``true``
     - 整體 RAG 開關。
   * - ``PRTHINKER_REMOTE_RAG``
     - ``true``
     - 用伺服器端 ``/rag`` 而非在本機載入 FAISS（省 runner 記憶體）。
   * - ``PRTHINKER_GATE_ON``
     - ``error``
     - 哪一級嚴重度會讓 Check Run 變 ``failure``\ ：
       ``none`` / ``warning`` / ``error``\ 。
   * - ``PRTHINKER_INCLUDE_CI_SIGNALS``
     - ``true``
     - 把失敗 job 的尾端 log 前置到 diff。
   * - ``PRTHINKER_RULES_DIR``
     - *(未設)*
     - Per-repo ``*.md`` 規則檔的路徑。

完整變數與對應 CLI flag 在 :doc:`configuration` 與
:doc:`../reference/cli`。

Branch protection
-----------------

讓 reviewer 真的能擋合併：

1. 跑至少一次 ``PRTHINKER_GATE_ON=error`` 的 PR──PR 的 Checks 分頁就會出現
   ``prthinker`` 這個 check。
2. 到 **Settings → Branches → branch protection rule**\ ，選你的 ``main``
   （或目標 branch）。
3. 啟用 **Require status checks to pass before merging**\ ，把
   ``prthinker`` 加進必要檢查。

之後，只要 PR 還有至少一筆 ``error`` 嚴重度的 finding 就無法合併，直到：

* 作者處理該 finding（並透過推新 commit 或重新觸發來重跑）；或者
* Maintainer 強制覆寫該 check。

總結留言會顯示 error / warning / info 的數量分佈，作者就能直接看到是哪一級
踩到 gate。

讓觸發等待 CI 完成
------------------

預設的 ``pull_request`` trigger 推 commit 後馬上跑。如果你想讓 reviewer
等 CI 完成才跑（這樣才能看到 CI 失敗 log），改成：

.. code-block:: yaml

   on:
     workflow_run:
       workflows: ["CI"]
       types: [completed]

在 ``workflow_run`` 模式下要從 run payload 取得 PR 編號，請參考 GitHub
Actions 對 ``workflow_run`` context 的說明。

Self-hosted GPU runner（可選）
------------------------------

如果你想跳過遠端伺服器，直接在 runner 上跑推論，就需要一台有 CUDA GPU 的
self-hosted runner。\ ``ubuntu-latest``\ （GitHub-hosted）裝不下 30B。

Workflow 範例：

.. code-block:: yaml

   jobs:
     prthinker:
       runs-on: [self-hosted, gpu]
       env:
         PRTHINKER_BACKEND: local
         PRTHINKER_MODEL_NAME: Qwen/Qwen3-Coder-30B-A3B-Instruct
         PRTHINKER_LORA_PATH: ../train/outputs-lora-qwen3-coder-30b
         PRTHINKER_USE_REMOTE_PIPELINE: "false"
         PRTHINKER_REMOTE_RAG: "false"
       steps:
         - uses: actions/checkout@v4
         - run: pip install -e ".[local]"
         - run: python -m prthinker review-pr

flag 都一樣，只是每個檔案要 5-10 分鐘（vs 配好的伺服器上的約 30 秒）。
