組態
====

每個 CLI flag 都有對應的環境變數。CLI 參數優先於環境變數，環境變數優先於
套件預設。組態在啟動時就會驗證──不合法的組合直接拋例外，不會偷偷退化。

Backend 選擇
------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - 環境變數
     - 預設
   * - ``--backend {local,remote,openai,anthropic,gemini,cohere,mistral,claude-cli,codex-cli}``
     - ``PRTHINKER_BACKEND``
     - ``remote``
   * - ``--remote-url URL``
     - ``PRTHINKER_REMOTE_URL``
     - *(remote 時必填)*
   * - ``--remote-api-key TOKEN``
     - ``PRTHINKER_REMOTE_API_KEY``
     - *(未設)*
   * - ``--remote-timeout SECONDS``
     - ``PRTHINKER_REMOTE_TIMEOUT``
     - ``600``
   * - ``--use-remote-pipeline``
     - ``PRTHINKER_USE_REMOTE_PIPELINE``
     - ``false``
   * - ``--model-name NAME``
     - ``PRTHINKER_MODEL_NAME``
     - ``Qwen/Qwen3-Coder-30B-A3B-Instruct``
   * - ``--lora-path PATH``
     - ``PRTHINKER_LORA_PATH``
     - *(未設)*

``--use-remote-pipeline`` 每個檔案只呼叫一次 ``/review``\ ，而不是 runner 上
迴圈打 ``/ask``\ 。這樣比較快、且把 prompt 編排集中在伺服器，缺點是綁住
runner 必須對應有 ``/review`` endpoint 的伺服器版本。

OpenAI 相容供應商（\ ``--backend openai``\ ）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

這一個 backend 對接任何實作 OpenAI ``POST /chat/completions`` 形狀的
服務──OpenAI 本家、Azure OpenAI、vLLM、Ollama（\ ``/v1``\ ）、LM Studio、
llama.cpp server、Together AI、Groq、DeepInfra、OpenRouter ……

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - 環境變數
     - 預設
   * - ``--openai-model NAME``
     - ``PRTHINKER_OPENAI_MODEL``
     - ``gpt-4o-mini``
   * - ``--openai-api-key TOKEN``
     - ``PRTHINKER_OPENAI_API_KEY`` / ``OPENAI_API_KEY``
     - *(必填)*
   * - ``--openai-base-url URL``
     - ``PRTHINKER_OPENAI_BASE_URL``
     - ``https://api.openai.com/v1``
   * - ``--openai-organization ID``
     - ``PRTHINKER_OPENAI_ORGANIZATION`` / ``OPENAI_ORG_ID``
     - *(未設)*

Anthropic Claude（\ ``--backend anthropic``\ ）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - 環境變數
     - 預設
   * - ``--anthropic-model NAME``
     - ``PRTHINKER_ANTHROPIC_MODEL``
     - ``claude-opus-4-7``
   * - ``--anthropic-api-key TOKEN``
     - ``PRTHINKER_ANTHROPIC_API_KEY`` / ``ANTHROPIC_API_KEY``
     - *(必填)*
   * - ``--anthropic-base-url URL``
     - ``PRTHINKER_ANTHROPIC_BASE_URL``
     - ``https://api.anthropic.com``
   * - ``--anthropic-version VER``
     - ``PRTHINKER_ANTHROPIC_VERSION``
     - ``2023-06-01``

本機 agent CLI（\ ``--backend claude-cli``\ ）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

以非互動 print 模式（\ ``claude -p``\ ）執行本機安裝的 ``claude`` CLI，
每次生成起一個子行程。Prompt 走 stdin 傳入──審查 prompt 內嵌整份 diff，
當命令列參數會撞上 Windows 的長度上限──回應則要求
``--output-format json``\ ，讓結果文字與 token 用量能確定性解析
（純文字輸出會原樣退回）。

與 HTTP backend 不同，CLI 可透過 ``--claude-cli-allowed-tools``
（轉送為 ``--allowedTools``\ ）取得工具集，讓審查能以完整的本機工具鍊
查閱工作樹──讀檔、grep、追 import──而不是只看 prompt 文字。
``--claude-cli-workdir`` 界定工具作用的目錄。

.. list-table::
   :header-rows: 1
   :widths: 38 34 28

   * - CLI flag
     - 環境變數
     - 預設
   * - ``--claude-cli-path PATH``
     - ``PRTHINKER_CLAUDE_CLI_PATH``
     - ``claude``
   * - ``--claude-cli-model NAME``
     - ``PRTHINKER_CLAUDE_CLI_MODEL``
     - *(CLI 自身預設)*
   * - ``--claude-cli-workdir PATH``
     - ``PRTHINKER_CLAUDE_CLI_WORKDIR``
     - ``.``
   * - ``--claude-cli-allowed-tools LIST``
     - ``PRTHINKER_CLAUDE_CLI_ALLOWED_TOOLS``
     - *(未設──沿用 CLI 自身工具政策)*
   * - ``--claude-cli-timeout SECONDS``
     - ``PRTHINKER_CLAUDE_CLI_TIMEOUT``
     - ``3600``

本機 agent CLI（\ ``--backend codex-cli``\ ）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

以 headless 模式執行本機安裝的 ``codex`` CLI（\ ``codex exec --json
--skip-git-repo-check -C <workdir> -``\ ），每次生成起一個子行程。
Prompt 走 stdin 傳入（結尾的 ``-``\ ）；輸出為 NDJSON，最後一個
``agent_message`` 事件即為答案，token 用量取自 ``turn.completed``\ 。

Sandbox 模式預設 ``read-only``\ ：CLI 可用自身工具鍊讀取工作樹，但
絕不改動它。受信任的環境可改用 ``workspace-write`` 或
``danger-full-access``\ 。

.. list-table::
   :header-rows: 1
   :widths: 38 34 28

   * - CLI flag
     - 環境變數
     - 預設
   * - ``--codex-cli-path PATH``
     - ``PRTHINKER_CODEX_CLI_PATH``
     - ``codex``
   * - ``--codex-cli-model NAME``
     - ``PRTHINKER_CODEX_CLI_MODEL``
     - *(CLI 自身預設)*
   * - ``--codex-cli-workdir PATH``
     - ``PRTHINKER_CODEX_CLI_WORKDIR``
     - ``.``
   * - ``--codex-cli-sandbox {read-only,workspace-write,danger-full-access}``
     - ``PRTHINKER_CODEX_CLI_SANDBOX``
     - ``read-only``
   * - ``--codex-cli-timeout SECONDS``
     - ``PRTHINKER_CODEX_CLI_TIMEOUT``
     - ``3600``

多模型仲裁
----------

預設關閉。開啟 ``--arbitration`` 後，``--arbitration-backends`` 列出的
每個 backend 會重新評判主模型的 inline findings：每個仲裁者收到
findings 清單加 diff，逐條投 ``confirm`` / ``reject``\ ，再由策略合併
票數──被否決的 finding 在發文前就被剔除。

每個仲裁者沿用它作為主 backend 時的同一組 flags / 環境變數
（\ ``openai`` 仲裁者讀 ``--openai-*``\ ，``claude-cli`` 仲裁者讀
``--claude-cli-*``\ ，依此類推）。

這一層採 fail-open：仲裁者出錯或輸出不可解析視為棄權，沒有任何有效票
的 finding 一律保留。仲裁只會刪噪音──不會因仲裁者不穩而弄丟 finding。

.. list-table::
   :header-rows: 1
   :widths: 42 34 24

   * - CLI flag
     - 環境變數
     - 預設
   * - ``--arbitration``
     - ``PRTHINKER_ARBITRATION``
     - ``false``
   * - ``--arbitration-backends a,b``
     - ``PRTHINKER_ARBITRATION_BACKENDS``
     - *(未設)*
   * - ``--arbitration-strategy {majority,unanimous,any}``
     - ``PRTHINKER_ARBITRATION_STRATEGY``
     - ``majority``
   * - ``--arbitration-max-new-tokens N``
     - ``PRTHINKER_ARBITRATION_MAX_NEW_TOKENS``
     - ``4096``

``majority`` 只有 reject 多於 confirm 才剔除（平手保留），
``unanimous`` 只要有一票 reject 就剔除，``any`` 只要有一票 confirm
就保留。

由兩個本機 agent CLI 組成仲裁小組的多模型審查
（完整腳本見 ``examples/multi-model-review.sh``\ ）：

.. code-block:: bash

   prthinker review-pr \
       --repo owner/name --pr-number 42 \
       --per-file --inline-review \
       --arbitration \
       --arbitration-backends claude-cli,codex-cli \
       --arbitration-strategy majority

RAG 與規則
----------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - 環境變數
     - 預設
   * - ``--no-rag``
     - ``PRTHINKER_RAG_ENABLED=false``
     - RAG 開啟
   * - ``--remote-rag``
     - ``PRTHINKER_REMOTE_RAG``
     - ``false``
   * - ``--rag-threshold FLOAT``
     - ``PRTHINKER_RAG_THRESHOLD``
     - ``0.7``
   * - ``--rules-dir PATH``
     - ``PRTHINKER_RULES_DIR``
     - *(未設)*

``--remote-rag`` 讓 runner 呼叫伺服器的 ``/rag``\ ，不在本機載入 4B embedding
模型──預設的 GitHub-hosted runner 必須開這個。

``--rules-dir`` 會把指定目錄下的每個 ``*.md`` 都視為一條常駐團隊規則，
排在 RAG 檢索出來的規則之後。

逐檔模式與 inline review
------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - CLI flag
     - 環境變數
     - 預設
   * - ``--per-file``
     - ``PRTHINKER_PER_FILE``
     - ``false``
   * - ``--inline-review``
     - ``PRTHINKER_INLINE_REVIEW``
     - ``false``
   * - ``--max-findings-per-file N``
     - ``PRTHINKER_MAX_FINDINGS_PER_FILE``
     - ``10``
   * - ``--exclude-globs PATTERNS``
     - ``PRTHINKER_EXCLUDE_GLOBS``
     - *(未設)*
   * - ``--target-file PATH``
     - ``PRTHINKER_TARGET_FILE``
     - *(未設)*

Inline review 需要先啟用 per-file 模式（inline-findings step 需要知道
正在審哪個檔）。光開 ``--inline-review`` 而沒有 ``--per-file`` 不會壞，
只是不會有效果。

``--exclude-globs`` 是逗號分隔之 fnmatch patterns（例如
``.idea/*,datas/*,*.md,*.lock``\ ）。parse 出的 diff 中匹配任一
pattern 之 path 在 per-file loop 前就被丟掉──IDE state、生成
資料、大段文件變更等不浪費 GPU 時間。

``--target-file`` 把 per-file loop 限定在單一精確 path。搭
``--output-json`` 讓 CI matrix shard 各自接管一個 file 之 review
（matrix workflow 見 :doc:`github-actions`\ ）。

Matrix 分片與 aggregation
-------------------------

對於把 per-file review 切到多 runner 之 workflow（CI matrix 或外
部 job queue），每個 shard 跑 ``review-pr`` 之 *partial* 模式，最
後一個 aggregator 把所有 shard 之 findings 合一成單一 PR-level
review。

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - CLI flag
     - 環境變數
     - 預設
   * - ``--output-json PATH``
     - ``PRTHINKER_OUTPUT_JSON``
     - *(未設)*
   * - ``--aggregate-from DIR``
     - ``PRTHINKER_AGGREGATE_FROM``
     - *(未設)*

``--output-json`` 讓 ``review-pr`` 從「post 到 GitHub」改為「把
partial ``ReviewResult`` 序列化到磁碟」。Shard 仍正常跑 pipeline
但**不**做 summary comment upsert、inline review submit、gate
open，這些交給 ``aggregate`` 子指令──它讀 ``--aggregate-from``
下所有 JSON 後合一 post。

合併前 gate
-----------

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - CLI flag
     - 環境變數
     - 預設
   * - ``--gate-on {none,warning,error}``
     - ``PRTHINKER_GATE_ON``
     - ``none``

詳見 :doc:`../concepts/ci-and-gate`。設成 ``none`` 為純建議模式，設成
``error`` 則只要有 error 嚴重度的 finding 就讓 Check Run failure。

CI 訊號
-------

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - CLI flag
     - 環境變數
     - 預設
   * - ``--include-ci-signals``
     - ``PRTHINKER_INCLUDE_CI_SIGNALS``
     - ``false``
   * - ``--ci-signal-max-jobs N``
     - ``PRTHINKER_CI_SIGNAL_MAX_JOBS``
     - ``5``
   * - ``--ci-signal-tail-chars N``
     - ``PRTHINKER_CI_SIGNAL_TAIL_CHARS``
     - ``4000``

訊號透過 platform adapter 取得：GitHub 讀失敗的 Actions job log，
GitLab 讀失敗 pipeline job 的 trace。沒有 CI API 的平台會記一行 log
後跳過。

伺服器端
--------

這些變數是由 ``codes/run/fastapi_server.py`` 在啟動時讀取的，\ **不是** runner
CLI 在讀。

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - 環境變數
     - 效果
   * - ``PRTHINKER_DISMISSED_PATH``
     - ``dismissed.jsonl`` 路徑。未設 / 不存在 → 過濾器關閉。
   * - ``PRTHINKER_DISMISSED_THRESHOLD``
     - 丟棄重複命中所用的 cosine similarity 下限。預設 ``0.85``\ 。
   * - ``PRTHINKER_ACCEPTED_PATH``
     - ``accepted.jsonl`` 路徑。未設 / 不存在 → 不注入範例。
   * - ``PRTHINKER_ACCEPTED_THRESHOLD``
     - 採納為 top-K 範例的 cosine 下限。預設 ``0.6``\ 。
   * - ``PRTHINKER_ACCEPTED_TOP_K``
     - 注入幾條範例。預設 ``3``\ 。

輸出與 logging
--------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - 環境變數
     - 預設
   * - ``--log-level LEVEL``
     - ``PRTHINKER_LOG_LEVEL``
     - ``INFO``
   * - ``--steps a,b,c``
     - *(無)*
     - *(全部註冊的 step)*
   * - ``--max-new-tokens N``
     - ``PRTHINKER_MAX_NEW_TOKENS``
     - ``32768``
   * - ``--output-dir PATH``
     - *(只在 review-file)*
     - *(無)*
