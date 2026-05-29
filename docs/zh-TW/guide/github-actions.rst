GitHub Actions 整合
===================

Reviewer 內附一份可直接用的 workflow：\ ``.github/workflows/prthinker.yml``\ 。
它在 ``pull_request`` ``opened`` / ``synchronize`` / ``reopened`` 時觸發，
透過同一個 PR 回貼 review。

Workflow 結構
-------------

Workflow 拆成三個 job，避免某個慢檔案或大 PR 卡死整段 review：

1. **enumerate**（5 分鐘）— 列出 PR 改動的 files，依
   ``PRTHINKER_EXCLUDE_GLOBS`` 過濾 noise paths，把剩下的清單以 JSON
   output 傳給下一個 job 的 matrix。
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
