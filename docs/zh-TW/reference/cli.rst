CLI 參考
========

CLI 可透過已安裝的 entry point 或 module 兩種方式呼叫::

   prthinker <subcommand> [options]
   python -m prthinker <subcommand> [options]

全域選項
--------

.. option:: --log-level {DEBUG,INFO,WARNING,ERROR}

   預設 ``INFO``\ 。可用 ``PRTHINKER_LOG_LEVEL`` 覆寫。

review-pr
---------

抓 PR diff、跑 pipeline、貼留言 + review + gate。

.. code-block:: text

   prthinker review-pr
       --repo OWNER/NAME           # 或 $GITHUB_REPOSITORY
       --pr-number N
       --github-token TOKEN        # 或 $GITHUB_TOKEN
       [--backend {local,remote,openai,anthropic,gemini,cohere,mistral,claude-cli,codex-cli}]
       [--remote-url URL]
       [--use-remote-pipeline]
       [--no-rag] [--remote-rag] [--rag-threshold 0.7]
       [--rules-dir PATH]
       [--per-file] [--inline-review] [--max-findings-per-file 10]
       [--step-plan {full,adaptive}]
       [--review-preset {none,backend,frontend,security,release}]
       [--repo-context-strategy STRATEGY] [--calibration-gate]
       [--reply-to-author] [--counterfactual] [--provenance]
       [--diff-since-last] [--diff-cache-path PATH]
       [--verify-suggestions] [--verify-cmd CMD] [--verify-timeout 60] [--verify-workdir PATH]
       [--api-consistency] [--pr-classify] [--reproducibility-check]
       [--dep-upgrade-check]
       [--personas LIST] [--risk-weighted] [--risk-workdir PATH] [--diff-entropy]
       [--judge] [--self-correct]
       [--arbitration] [--arbitration-backends a,b]
       [--arbitration-strategy {majority,unanimous,any}]
       [--gate-on {none,warning,error}]
       [--include-ci-signals] [--ci-signal-max-jobs 5] [--ci-signal-tail-chars 4000]
       [--marker '<!-- prthinker:summary -->']
       [--dry-run]

值得注意的 flag：

* ``--dry-run``\ ──把總結留言印到 stdout 而不貼上去，也跳過 Check Run。
* ``--marker``\ ──upsert PR 留言用的 sentinel HTML comment。只有同一個
  repo 想跑多個 reviewer 時才需要覆寫。
* ``--exclude-globs``\ ──逗號分隔之 fnmatch patterns；
  ``--per-file`` 模式下匹配任一 pattern 的 file 會被跳過。對 IDE
  設定、生成資料、大段 markdown 是便宜防線，不浪費 GPU 時間。Env:
  ``PRTHINKER_EXCLUDE_GLOBS``\ 。
* ``--target-file``\ ──設了之後，\ ``--per-file`` 模式只 review 這
  個 diff path，其它檔案全跳過。讓 CI matrix runner 各自接管一個
  file，給每個 file 自己的 timeout budget；matrix workflow 細節
  見 :doc:`../guide/github-actions`\ 。Env: ``PRTHINKER_TARGET_FILE``\ 。
* ``--output-json``\ ──把 partial ``ReviewResult`` 寫成 JSON 而不
  post 到 GitHub。搭 matrix runner 的 ``--target-file``\ ，讓每個
  shard 把自己 file 的 findings 收成 artifact，後面的 ``aggregate``
  job 才合一處理。Env: ``PRTHINKER_OUTPUT_JSON``\ 。

研究級 flag（opt-in\ ，需搭配 ``--inline-review``）：

.. option:: --reply-to-author

   讀取 PR 作者對最近一則 prthinker 摘要評論的回覆\ ，並把它們以
   *Prior dialogue* 區塊注入 inline-findings prompt\ 。\ 把對話迴圈
   閉上\ ，避免下一次審查靜默重貼作者已回應過的評論\ 。環境變數：
   ``PRTHINKER_REPLY_TO_AUTHOR``\ 。

.. option:: --counterfactual

   在 inline findings 之後\ ，跑一個 counterfactual / mutation step\ ，
   對屬於\ *設計選擇*\ 之評論列出競爭性實作方案與 trade-off 矩陣\ 。
   明確 bug / nit 之 finding 會被跳過\ 。每個檔案多一次 backend 呼叫\ 。
   環境變數：``PRTHINKER_COUNTERFACTUAL``\ 。

.. option:: --provenance

   要求模型對每條 finding 引用 RAG 規則 / accepted-example /
   diff 行號\ ，並在 PR 每個檔案區塊下加上\ *Audit trail*\ 摘要\ 。
   越界之引用會被靜默丟棄\ ；壞引用絕不拖垮真評論\ 。環境變數：
   ``PRTHINKER_PROVENANCE``\ 。

.. option:: --walkthrough

   新增一個每檔 ``WalkthroughStep``\ ，就該檔變更寫出二至四句\
   「\ 做了什麼、為何\ 」\ 之敘事\ ，釘於該檔區塊最上方──為無推論之
   commit-message PR 概覽之推論側對應物\ 。它只描述（不評斷）\ ，只依賴
   diff\ ，故開不開 ``--inline-review`` 皆可執行\ 。環境變數：
   ``PRTHINKER_WALKTHROUGH``\ 。

.. option:: --judge

   每檔自評步驟\ ，輸出 ``approve`` / ``request_changes`` / ``comment``
   verdict\ 。CLI 跨檔聚合後映射為 GitHub review event\ 。

.. option:: --self-correct

   二次降噪：把存活之 findings 列給模型\ ，請它刪掉它認為是噪音的條目\ 。
   每檔多一次 backend 呼叫\ 。安全失敗方向：解析失敗時保留原清單\ 。

.. option:: --diff-since-last

   把每檔之新側內容 hash\ ，後續 push 時 hash 未變之檔直接 reuse 上次
   findings\ 。SQLite 儲存體於 ``--diff-cache-path``（預設
   ``.prthinker/diff-cache.sqlite``），key 為
   ``(pr_number, repo, file_path, hunk_sha256)`` —— 跨 PR 隔離\ 。環境變數：
   ``PRTHINKER_DIFF_SINCE_LAST``\ 。

.. option:: --verify-suggestions

   把 working tree 複製到 disposable sandbox\ ，於 finding 之 line range
   套用 ``suggestion`` block\ ，再以 ``--verify-cmd``\（預設
   ``pytest -x``）於 ``--verify-timeout``\（預設 60s）下執行\ ，把每條
   finding 標 ``[verified]`` / ``[FAILED]`` / ``[skipped]`` /
   ``[error]``\ 。原 repo 絕不動\ 。環境變數：
   ``PRTHINKER_VERIFY_SUGGESTIONS``\ 。

.. option:: --api-consistency

   當 diff 同時碰到後端（``.py``）與前端（``.ts`` / ``.tsx`` /
   ``.js`` / ``.jsx``）\ ，新增一個 step 偵測\ *跨檔*\ drift（重命名欄位、
   移除路由、類型變更）\ 。單語言 PR 上靜默 pass\ 。環境變數：
   ``PRTHINKER_API_CONSISTENCY``\ 。

.. option:: --pr-classify

   從 diff + 標題 + body 把 PR 分為 ``bugfix`` / ``feature`` /
   ``refactor`` / ``docs`` / ``chore`` / ``unknown``\ ，後續 review
   深度隨之調整：docs PR 跳 inline findings\ ；bugfix PR 用 focused
   prompt + 較小 budget\ 。環境變數：``PRTHINKER_PR_CLASSIFY``\ 。

.. option:: --reproducibility-check

   同 prompt 跑兩次 inline-findings step（非 0 temperature 自然產生
   第二樣本）\ ，每條 finding 按跨 pass match 標 ``stable`` / ``low``\ 。
   後端通用 uncertainty proxy\ 。環境變數：
   ``PRTHINKER_REPRODUCIBILITY_CHECK``\ 。

.. option:: --dep-upgrade-check

   偵測 lock-file（``requirements.txt`` / ``pyproject.toml`` /
   ``package.json``）中之版本 bump\ ，問模型該套件\ 之 breaking change
   是否影響本 repo 之實際用法\ 。環境變數：
   ``PRTHINKER_DEP_UPGRADE_CHECK``\ 。

.. option:: --personas <list>

   逗號分隔之 persona 名單（``security``\ 、``performance``\ 、
   ``readability``\ 、``api_stability``\ 、``maintainability``）── 或
   ``all`` 跑全 5 個\ 。每個 persona 之 prompt 限定模型只在該 lens 範圍內
   評論\ ；之後一個 conflict-finder step 找出跨 persona 之分歧\ 。空（預設）
   即停用\ 。環境變數：``PRTHINKER_PERSONAS``\ 。

.. option:: --risk-weighted

   以 churn（``git log`` 於預設 90 天 lookback）\ 、complexity（HEAD 行數）\ 、
   bug history（commit message 命中 ``fix:`` / ``bug`` / ``revert``）算
   每檔風險分\ ；按分數線性縮放 ``max_findings_per_file`` 於 ``floor``
   （預設 2）到 ``ceiling``（預設 ``2 × base_budget``）之間\ 。
   ``--risk-workdir`` 指向 git repo\ 。另外會在總結中附一個可展開的
   「\ high-risk files\ 」\ 註記（分數及其 churn／bug-fix／行數拆解）\ ，
   讓審查者看到歷史上最容易壞的檔案\ 。環境變數：
   ``PRTHINKER_RISK_WEIGHTED``\ 。

.. option:: --diff-entropy

   計算 diff 之 size + 目錄分布 Shannon entropy\ ；分數越過 ``bomb``
   閾值時於留言頂端貼\ 「\ Consider splitting this PR\ 」\ 警示\ 。純本機 CPU\ 、
   無 backend 呼叫\ 。環境變數：``PRTHINKER_DIFF_ENTROPY``\ 。

.. option:: --review-order

   加一個\ 「\ Suggested review order\ 」\ 註記\ ，用 repo knowledge graph
   的 import 邊把變更檔案按\ 「\ 被最多其他變更檔案依賴\ 」\ 排前面\ ，最
   地基的檔案標上\ 「\ start here\ 」\ ，讓審查者先讀基礎變更再讀其呼叫端\ 。
   Best-effort：KG store 不存在時略過\ 。環境變數：``PRTHINKER_REVIEW_ORDER``\ 。

.. option:: --change-map

   在留言內嵌一張小的 Mermaid 圖\ ，畫出\ *變更檔案之間*\ 的 import 邊
   （來自 repo knowledge graph）\ ，讓改動的結構一眼可見\ 。GitHub 原生
   渲染 ```mermaid`` 區塊\ 。變更檔案之間沒有 import 邊時略過\ 。
   環境變數：``PRTHINKER_CHANGE_MAP``\ 。

.. option:: --auto-file-issues {none,off-diff,all}

   把審查 findings 自動開成 issue tracker 上的 issue\ 。\ ``off-diff``
   只開落在 diff hunks *之外*\ 的 findings —— 這些是平台會拒絕以
   inline comment 張貼\ 、原本只能留在 summary 文字裡的發現\ 。
   ``all`` 則每個 finding 都開\ 。每張 issue 內文帶指紋 marker
   （path + category + 正規化 comment 的雜湊）\ ，重跑審查不會把同一個
   問題重複開單\ ；單次最多開 10 張新 issue\ 。支援 GitHub 與 GitLab\ ；
   best-effort —— API 失敗絕不弄壞審查本體\ 。預設 ``none``\ 。
   環境變數：``PRTHINKER_AUTO_FILE_ISSUES``\ 。

.. option:: --issue-labels <labels>

   自動開的 issue 要套的標籤\ ，逗號分隔（預設 ``prthinker``）\ 。
   環境變數：``PRTHINKER_ISSUE_LABELS``\ 。

.. option:: --step-plan {full,adaptive}

   逐檔審查深度\ 。\ ``full``\ （預設）對每個檔案跑完所有已設定的
   step\ ；\ ``adaptive`` 讓鏈的深度隨檔案縮放：

   * **skip** —— lockfile\ 、生成／vendored／minified 產物與純空白
     重排版：零模型呼叫\ 。
   * **trivial** —— 文件／設定檔（``.md``\ 、\ ``.rst``\ 、
     ``.json``\ 、\ ``.yaml`` ……）或變更 ≤ 5 行之 diff：批次
     findings-only pass\ ，一次模型呼叫最多合併 6 個檔案或 24K
     字元之 diff\ 。
   * **standard** —— 其餘檔案跑單一 ``unified_review`` 呼叫\ ，一次
     回 findings\ 、簡短 summary 與 verdict\ 。
   * **deep** —— 變更 ≥ 200 行\ 、或 ``--risk-weighted`` 啟用時
     risk 分數 ≥ 0.7 之檔案\ ，保留完整已設定之鏈\ 。

   縮減 tier 同時封頂生成預算（trivial 4096／standard 8192
   tokens）\ ；deep 保留完整 ``--max-new-tokens`` 預算\ 。環境變數：
   ``PRTHINKER_STEP_PLAN``\ 。

.. option:: --review-preset {none,backend,frontend,security,release}

   展開一組精選的 review mode 與安全檢查 —— 只是既有 flag 之薄
   包裝\ ，不是新的審查路徑\ 。\ ``backend`` 啟用 ``security``\ 、
   ``performance``\ 、\ ``test-coverage`` 三個 mode\ ，外加
   ``--api-consistency`` 與 ``--dep-upgrade-check``\ ；\ ``frontend``
   啟用 ``accessibility``\ 、\ ``performance``\ 、\ ``pii``\ 、
   ``test-coverage``\ ；\ ``security`` 啟用 ``security``\ 、
   ``secret-scan``\ 、\ ``pii``\ ，外加 ``--redact-secrets``\ ，且
   ``--gate-on`` 仍為 ``none`` 時提高為 ``warning``\ ；\ ``release``
   啟用 ``security`` 與 ``test-coverage``\ ，外加
   ``--api-consistency``\ 、\ ``--dep-upgrade-check``\ 、
   ``--diff-entropy``\ 、\ ``--reproducibility-check``\ 、
   ``--judge``\ 。preset 之 mode 會與明確給的 ``--review-modes``
   清單合併\ 。環境變數：``PRTHINKER_REVIEW_PRESET``\ 。

.. option:: --repo-context-strategy {none,lexical,semantic,structural,graph,rerank,block_rerank,iterative,query_rewrite,hypothesis,execution}

   本機逐檔審查之跨檔 repository context\ 。\ ``none``\ （預設）維持
   既有 prompt\ ；其它策略會從 work tree 檢索相關檔案並注入每個檔案
   之 prompt\ 。\ ``hypothesis`` 跑 model-in-the-loop 之
   propose-verify 定位迴圈：每輪由模型提出可疑之（path\ 、symbol\ 、
   行號）假設\ ，經靜態驗證（路徑／symbol 存在\ 、AST 行區間\ 、
   import-graph caller）\ ，被駁回之假設回饋為修正\ ，確認之位置
   排最前\ 。\ ``execution`` 以執行證據重排序：從變更／issue 文字
   挖出之 stack-trace frame\ ，與 spectrum-based fault localization
   （Ochiai／Tarantula\ ，對逐測試 coverage 計算\ ；failing test 以
   程式方式提供時經 subprocess 收集）及 lexical 基礎排名做
   reciprocal-rank fusion\ ，無任何訊號時退化為基礎 retriever\ 。
   調校 flag（各有對應之 ``PRTHINKER_REPO_CONTEXT_*``
   環境變數）：

   * ``--repo-context-workdir PATH`` —— 檢索與 import-graph context
     所用之 work tree（預設 ``.``\ ）\ 。
   * ``--repo-context-top-k N`` —— 檔案層級檢索最多考慮之檔案數
     （預設 10）\ 。
   * ``--repo-context-keep-ratio FLOAT`` —— lexical keep-ratio
     截斷\ ；\ ``0``\ （預設）保留固定 top-k 尾端\ 。
   * ``--repo-context-block-candidates N`` —— ``block_rerank`` /
     ``iterative`` 策略每檔之候選 block 數（預設 6）\ 。
   * ``--repo-context-votes N`` —— model-in-the-loop 檢索之
     self-consistency 票數（預設 1）\ 。
   * ``--repo-context-rounds N`` —— ``iterative`` 與 ``hypothesis``
     策略之最大輪數（預設 3）\ 。
   * ``--repo-context-focus-lines N`` —— block context 之可選行窗
     focus\ ；\ ``0``\ （預設）停用\ 。

   環境變數：``PRTHINKER_REPO_CONTEXT_STRATEGY``\ 。

.. option:: --calibration-gate

   讓 merge gate 尊重校準後的棄權（calibrated abstention）\ 。每條
   finding 對 feedback 校準儲存體（``--calibration-store``\ ）評分\ ；
   provenance confidence 低於該 repo／author／category 校準閾值之
   finding 視為\ *棄權*\ ：它仍出現在 summary 與各報告中\ ，但不再擋
   gate\ ，gate line 並附上 ``calibration abstained N from
   blocking``\ 。同組旋鈕 —— ``--calibration-store``\ （SQLite 儲存
   路徑）\ 、\ ``--calibration-author``\ 、
   ``--calibration-category``\ 、
   ``--calibration-min-samples``\ （預設 10）\ 、
   ``--calibration-half-life-days``\ （預設 90）——
   決定 posterior 由哪段 feedback 歷史計得\ 。環境變數：
   ``PRTHINKER_CALIBRATION_GATE``\ 。

review-file
-----------

對本機檔案或 stdin 跑 pipeline。

.. code-block:: text

   prthinker review-file PATH
       [--backend {local,remote,openai,anthropic,gemini,cohere,mistral,claude-cli,codex-cli}]
       [--remote-url URL] [--remote-api-key TOKEN]
       [--model-name NAME] [--lora-path PATH]
       [--no-rag] [--remote-rag] [--rag-threshold 0.7]
       [--rules-dir PATH]
       [--per-file] [--inline-review] [--max-findings-per-file 10]
       [--step-plan {full,adaptive}]
       [--review-preset {none,backend,frontend,security,release}]
       [--repo-context-strategy STRATEGY]
       [--counterfactual] [--provenance] [--judge] [--self-correct]
       [--diff-since-last] [--verify-suggestions]
       [--api-consistency] [--pr-classify] [--reproducibility-check]
       [--dep-upgrade-check] [--personas LIST]
       [--risk-weighted] [--diff-entropy]
       [--max-new-tokens 32768]
       [--steps a,b,c]
       [--output-dir PATH]

``PATH`` 可填 ``-`` 從 stdin 讀 diff。

``--output-dir`` 會把每個 step 的原始輸出增量寫入磁碟──批次實驗或除錯
長跑時很有用。

``--steps`` 是逗號分隔的 step 名稱清單；空（預設）就跑全部已註冊的 step。

triage
------

對一份 diff 跑完所有\ *無需模型*\ 的 orientation 訊號並印出非空區塊。不載入
任何 backend,故瞬間完成且僅需 runner profile——可作為 push 前的本機檢查,
或 GPU-free 的 CI gate,在完整 review 排程前先抓出衝突標記、Trojan-Source
字元、吞錯、重新命名、刪除、mode 變更、大段貼上、純格式變更、覆蓋缺口、
殘留 debug 與延遲工作標記\ 。

.. code-block:: text

   prthinker triage
       [--diff-file PATH | --staged | --against REF]
       [--exit-nonzero-on-signal]

預設從 stdin 讀 diff;\ ``--diff-file`` 從檔案讀,\ ``--staged`` 跑
``git diff --cached``\ ,\ ``--against REF`` 跑 ``git diff REF``\ （如
``origin/main``\ ）。加上 ``--exit-nonzero-on-signal`` 時,只要有任一訊號
觸發即 exit 1,可用以 gate CI 步驟;否則一律 exit 0(僅供參考)\ 。

.. code-block:: bash

   git diff origin/main | prthinker triage
   prthinker triage --staged --exit-nonzero-on-signal

此訊號集即 PR 留言摘要下方所呈現者;各區塊偵測內容見
:doc:`../concepts/research-extensions`\ 。

retrieval-report
----------------

把 content-safe 的檢索軌跡（review 執行時 ``--trajectory-out`` 追加
的 JSONL）渲染成 Markdown 或 JSON 稽核報告：各事件計數\ 、retrieve
與 retrieval-use 統計\ 、retrieved／used／cited 文件總數\ 、導出之
utilization 比率\ ，以及逐 path 之拆解\ 。純本機聚合 —— 不載入任何
backend\ ，也不暴露 prompt 或程式碼內容\ ，報告可安全附成 CI
artifact\ 。

.. code-block:: text

   prthinker retrieval-report INPUT
       [--format {markdown,json}]
       [--out PATH]

``INPUT`` 為軌跡 JSONL 檔\ 。\ ``--format`` 預設 ``markdown``\ ；
``--out`` 把報告寫入檔案而非 stdout\ 。

depth-eval
----------

比較 ``full`` 與 ``adaptive`` 兩種審查方案在本機 diff 語料上的差異\ ，
把發現品質的落差與模型呼叫、token 節省並列報告\ 。每份 diff 都跑兩次
—— 一次走 ``full`` step plan\ ，一次走 ``adaptive`` —— 經兩條獨立建置
的 pipeline\ ，故 backend、retriever 與 cache 之狀態不會在兩次執行間
外洩\ 。

.. code-block:: text

   prthinker depth-eval
       (--diffs-dir DIR | --diffs-jsonl PATH)
       [--out PATH]
       [--max-diffs N]
       [--backend {local,remote,openai,anthropic,gemini,cohere,mistral,claude-cli,codex-cli}]
       [--remote-url URL] [--remote-api-key TOKEN]

語料來源為互斥且必填的一組：

* ``--diffs-dir`` —— 一個放 ``*.diff`` / ``*.patch`` 檔的目錄\ ，每檔
  一份 unified diff\ ，依檔名順序讀取\ 。
* ``--diffs-jsonl`` —— 一份 JSONL 語料\ ，每行一個 ``{"diff": ...}``
  物件\ ；沒有非空 ``diff`` 字串的列會被拒絕\ 。

``--max-diffs N`` 封頂比較的 diff 數（``0`` 為預設\ ，即不設限）\ 。
``--out`` 把 Markdown 報告寫入檔案\ ；省略時印至 stdout\ 。Backend 與
審查 flag 沿用共用的 common parser\ ，與各 review 子指令相同\ 。

報告會把兩次執行的每條 finding 配對\ ，並記錄：

* **finding 重疊** —— matched、missing（``full`` 有但 ``adaptive``
  丟掉）與 extra（只有 ``adaptive``）之計數\ 。
* **gate 嚴重度召回率** —— adaptive 保留了 full 執行中多少比例的
  error／warning finding\ ；此為判斷深度裁剪是否曾丟掉會擋 gate 的
  finding 的指標\ 。
* **adaptive tier 分布** —— 各深度 tier（skip／trivial／standard／
  deep）各認領了幾個檔案\ 。
* **各方案用量** —— 每個方案的模型呼叫數與 token 數\ ，外加逐 diff
  的 finding 數與呼叫數拆解\ 。

每個方案各拿一條全新建置的 pipeline 且停用 review 快取\ ，故一個方案
的快取 finding 絕不會污染另一個\ 。

aggregate
---------

把 ``review-pr --output-json`` 各 runner 寫出的 partial review JSON
合一，post 出單一 summary + inline review + gate close。對應到
:doc:`../guide/github-actions` 描述的 matrix workflow。

.. code-block:: text

   prthinker aggregate
       --repo OWNER/NAME
       --pr-number N
       --github-token TOKEN
       --aggregate-from DIR
       [--marker '<!-- prthinker:summary -->']
       [--inline-review] [--judge]
       [--gate-on {none,warning,error}]
       [--platform {github,gitlab}]
       [--dry-run]

Aggregator 會遞迴掃 ``--aggregate-from`` 下所有 ``*.json``\ （所以
``actions/download-artifact`` 常見的「一個 matrix iteration 一個
資料夾」 layout 無須額外接線），反序列化每個 partial 為 ``ReviewResult``\ ，
依 path 對 ``per_file`` 去重（同路徑 last-write-wins），跨 shard 合
``inline_findings`` + ``step_outputs`` + ``rag_docs``\ 。合完後另以
``/ask/submit`` 對 backend 取一段 3-5 句之 PR-wide overall summary，
塞進 ``step_outputs["total_summary"]``\ 並由 formatter 渲染為 PR 留言
頂部之 ``### Overall Summary``\ 。Post 路徑與 ``review-pr`` 完全相同
──同樣的 comment marker upsert、同樣的 ``submit_inline_review`` event
mapping（\ ``--judge`` 開啟時做 verdict aggregation）、同樣的 gate
close。

若目錄下沒有 JSON（例如所有 matrix shard 因 backend 不通而 skip），
指令 log 一則 warning 並 exit 0；workflow 端 fallback 之 shell step
會用同一個 marker 貼一則「skipped」notice。

Env equivalents: ``PRTHINKER_AGGREGATE_FROM``\ （input dir）、
``PRTHINKER_COMMENT_MARKER``\ （marker）、``PRTHINKER_GATE_ON``\ （gate
floor）。其餘由標準 ``GITHUB_REPOSITORY``\ 、\ ``PRTHINKER_PR_NUMBER``\ 、
``GITHUB_TOKEN`` 涵蓋。

pr-summary
----------

從 PR 標題、描述、commit 訊息與 diff 產生 Copilot 式 PR 摘要，並以專屬
marker ``<!-- prthinker:pr-summary -->`` upsert 成一則獨立留言（與
review summary 分開）。設計為在逐檔審查\ *之前*\ 執行──由
:doc:`../guide/github-actions` 之 ``enumerate`` job 呼叫──讓 reviewer
在較慢的審查進行時即有概覽。

.. code-block:: text

   prthinker pr-summary
       --repo OWNER/NAME            # 或 $GITHUB_REPOSITORY
       --pr-number N                # 或 $PRTHINKER_PR_NUMBER
       --github-token TOKEN         # 或 $GITHUB_TOKEN
       [--backend {local,remote,openai,anthropic,gemini,cohere,mistral,claude-cli,codex-cli}]
       [--remote-url URL] [--remote-api-key TOKEN]
       [--platform {github,gitlab,gitea}]
       [--dry-run]

它核對作者「所寫」（標題、body、commit 主旨）與 diff「所做」是否一致，
並被要求點出任何落差。輸出為 GitHub-flavoured Markdown，含
``### Overview``\ 、\ ``### Key changes``\ 、\ ``### Areas to review``
與 ``### Notes`` 等區段。

設計上為 best-effort：生成走注入之 backend，遇短暫故障（5xx、連線中
斷、空回應）會重試數次；持續失敗則 log warning 並 exit 0，使不穩定之
backend 永不阻擋 review matrix。``--dry-run`` 將渲染後之留言印至 stdout
而不貼出。

Env equivalents：``PRTHINKER_BACKEND``\ / ``PRTHINKER_REMOTE_URL``\ /
``PRTHINKER_REMOTE_API_KEY`` 選擇 backend；``GITHUB_REPOSITORY``\ 、
``PRTHINKER_PR_NUMBER``\ 、\ ``GITHUB_TOKEN`` 涵蓋目標。

harvest-dismissed
-----------------

掃 PR／MR review comment，把 dismissed finding 追加到 JSONL store。

.. code-block:: text

   prthinker harvest-dismissed
       [--platform github|gitlab]
       [--platform-base-url URL]
       --repo OWNER/NAME
       --github-token TOKEN
       [--pr-number N | --max-prs 50]
       [--out .prthinker/dismissed.jsonl]

設 ``--pr-number`` 時只掃那一個 PR／MR；否則迭代最近 ``--max-prs`` 個依
更新時間排序的 closed PR／MR。GitHub 上，review comment 帶 👎 reaction
或帶駁回關鍵字的回覆即視為 dismissed；GitLab 上則從 MR 的 diff
discussion 與 award emoji 讀取同樣的訊號。``--repo``\ ／
``--github-token`` 預設讀 ``GITHUB_REPOSITORY``\ ／``GITHUB_TOKEN``\ ，
並回退到 ``CI_PROJECT_PATH``\ ／``GITLAB_TOKEN``\ 。

harvest-accepted
----------------

掃 PR／MR 看是否有套用過的 suggestion 區塊，追加到 JSONL store。

.. code-block:: text

   prthinker harvest-accepted
       [--platform github|gitlab]
       [--platform-base-url URL]
       --repo OWNER/NAME
       --github-token TOKEN
       [--pr-number N | --max-prs 50]
       [--out .prthinker/accepted.jsonl]

當 PR 的任一 commit message 以 ``Apply suggestion(s) from code review``
開頭時即視為「有採納過建議」（GitLab 另外比對其原生的
``Apply N suggestion(s) to M file(s)`` 訊息）。每個帶 ```suggestion```
區塊的留言／diff note 都會保留。

adversarial-eval
----------------

把 prompt-injection 語料丟給目前 backend\ ，將每一筆呼叫之結果寫入
SQLite\ 。本子指令\ **不輸出**\ 任何彙總偵測率 —— 聚合計算交給下游 SQL\ ，
原始輸出保留以利稽核\ 。

.. code-block:: text

   prthinker adversarial-eval
       --corpus PATH                # JSONL 語料（參考 seed.jsonl）
       --outcomes-path PATH         # SQLite 輸出檔
       [--backend {local,remote,openai,anthropic,gemini,cohere,mistral,claude-cli,codex-cli}]
       [--remote-url URL] [--remote-api-key TOKEN]
       [--openai-model NAME] [--openai-api-key TOKEN]
       [--anthropic-model NAME] [--anthropic-api-key TOKEN]
       [--max-new-tokens 4096]

語料格式：每行一個 JSON 物件\ ，符合
:class:`prthinker.adversarial.AttackCase`\ 。隨附之
``prthinker/adversarial_corpus/seed.jsonl`` 是手工撰寫的種子\ ，
涵蓋四種攻擊類型（``direct_injection`` / ``encoded_payload`` /
``split_injection`` / ``role_hijack``）—— 它\ **不**\ 是 benchmark\ 。

outcomes 表 schema：

.. code-block:: sql

   CREATE TABLE outcomes (
     id          INTEGER PRIMARY KEY AUTOINCREMENT,
     timestamp   REAL    NOT NULL,
     case_id     TEXT    NOT NULL,
     category    TEXT    NOT NULL,
     backend     TEXT    NOT NULL,
     model       TEXT    NOT NULL,
     bypassed    INTEGER NOT NULL,   -- 0/1
     detected    INTEGER NOT NULL,   -- 0/1
     success_markers_hit   TEXT NOT NULL,  -- 逗號連接
     detection_markers_hit TEXT NOT NULL,
     output      TEXT    NOT NULL,
     error       TEXT
   );

issue-fix
---------

針對一個 issue 定位相關檔案\ 、提出經驗證的 find/replace 編輯\ ，
並以 JSON 印出\ 。預設唯讀：除非給 ``--apply`` 或 ``--test-cmd``\ ，
否則絕不寫入 work-tree\ 。

.. code-block:: text

   prthinker issue-fix "issue 文字"        # 或 '-' 讀 stdin
       --workdir PATH                       # repository work-tree
       [--issue-file PATH]
       [--retriever {graph-rerank,graph,rerank,lexical}]
       [--top-k 10] [--max-retries 1]
       [--backend {local,remote,openai,anthropic,gemini,cohere,mistral,claude-cli,codex-cli}]
       [--output PATH] [--patch PATH]
       [--apply] [--test-cmd CMD] [--test-timeout 600]

每個提出的編輯都必須能逐字套用\ ，且套用後檔案語法有效（Python）\ ；
無效的批次會附上失敗原因重問一次\ 。\ ``--patch`` 寫出 unified diff\ ，
``--apply`` 把編輯寫入 work-tree\ ，\ ``--test-cmd`` 套用修復後執行該
指令作為 Pass@1 檢查（失敗時 exit 1）\ 。

issue-autofix
-------------

從 issue tracker（GitHub 或 GitLab）抓 issue\ ，用與 ``issue-fix``
相同的引擎提出經驗證的修復\ ；加上 ``--open-pr`` 時會套用\ 、commit\ 、
push\ ，開一個內文帶 ``Fixes #N`` 的 fix pull / merge request\ ，並把
連結留言回 issue\ 。不加 ``--open-pr`` 則是 dry run：只以 JSON 印出
提案與 patch\ ，不改動任何東西\ 。

.. code-block:: text

   prthinker issue-autofix
       --repo OWNER/NAME                    # GitLab：project 路徑或 id
       --workdir PATH                       # scratch clone（--open-pr 時會被改動）
       (--issue-number N | --issue-label LABEL [--limit 3])
       [--platform {github,gitlab}] [--gitlab-url URL]
       [--github-token TOKEN]               # 或 $GITHUB_TOKEN / $GITLAB_TOKEN
       [--retriever {graph-rerank,graph,rerank,lexical}]
       [--top-k 10] [--max-retries 1]
       [--open-pr] [--no-draft]
       [--base-branch NAME] [--branch-prefix issue-fix]
       [--test-cmd CMD] [--test-timeout 600]
       [--output PATH]

重點行為：

* ``--test-cmd`` 是一道閘門：指令對套用後的修復執行失敗時\ ，不會
  push 分支\ 、不會開 PR —— 結果記錄 ``test command failed``\ 。
* fix PR / MR 預設是 **draft**\ （``--no-draft`` 直接開成待審）\ ；
  合併後 ``Fixes #N`` 自動關閉 issue\ 。
* ``--issue-label`` 批次模式在 issue 之間還原起始 git ref\ ，一個修復
  不會滲入下一個\ ；單一 issue 失敗會記錄錯誤結果\ ，批次繼續\ 。
* ``--workdir`` 請指向一個專用的 scratch clone\ ，其 ``origin``
  remote 必須是 token 能 push 的 —— 迴圈會在裡面執行
  ``git checkout -B``\ 、\ ``commit``\ 、\ ``push --force-with-lease``\ 。
* 只有所有嘗試的 issue 都產出有效修復時\ ，exit code 才是 ``0``\ 。

Exit code
---------

* ``0``\ ──成功（含 dry-run 與零 finding 的情況）。
* ``1``\ ──runtime 失敗（network、GPU、parse error）。\ ``--gate-on`` 啟用時，
  Check Run 在傳遞錯誤前會被 PATCH 為 ``failure``\ 。
* ``2``\ ──argparse 參數解析或驗證錯誤。
