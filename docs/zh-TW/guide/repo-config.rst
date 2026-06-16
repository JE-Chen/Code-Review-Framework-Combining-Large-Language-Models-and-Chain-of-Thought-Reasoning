Repo 層級組態
=============

把 ``.prthinker.yaml`` 放在 repo 根目錄，可以集中管理所有非密鑰類設定。
CLI 每次啟動會自動讀取，當作環境變數與 CLI flag 之下的預設層。

解析順序（越下面越優先）
------------------------

1. 套件內建預設。
2. 當前目錄的 ``.prthinker.yaml``\ （或 ``--config PATH``\ ）。
3. 環境變數（\ ``PRTHINKER_*``\ 、\ ``OPENAI_API_KEY``\ ……）。
4. 命令列 flag。

**密鑰絕對不放 YAML。** API key、token、GitHub token 一律只從環境變數讀取，
這樣 commit 進 git 的 config 檔不會洩漏 credential。

Schema
------

.. code-block:: yaml

   # .prthinker.yaml — 把所有開關都打開的範例
   backend: openai                # local | remote | openai | anthropic
   max_new_tokens: 32768

   per_file: true
   inline_review: true
   max_findings_per_file: 10

   rag:
     enabled: true
     threshold: 0.7
     rules_dir: ./team-rules      # 可選；*.md 檔變成團隊規則
     remote: false                # 改打伺服器 /rag、不在本機載 FAISS

   gate:
     severity: error              # none | warning | error
                                  # 注意：用 'severity' 不要用 'on'，
                                  # YAML 1.1 會把 `on` 解析成 boolean True。

   ci_signals:
     enabled: true
     max_jobs: 5
     tail_chars: 4000

   cache:
     enabled: true
     path: .prthinker/cache.sqlite
     ttl_days: 7                  # 設成 null 關掉 TTL

   telemetry:
     enabled: true
     path: .prthinker/telemetry.sqlite

   stores:
     dismissed: .prthinker/dismissed.jsonl
     accepted: .prthinker/accepted.jsonl

   local:
     model: Qwen/Qwen3-Coder-30B-A3B-Instruct
     lora_path: ../train/outputs-lora-qwen3-coder-30b

   openai:
     model: gpt-4o-mini
     base_url: https://api.openai.com/v1
     # api_key 來自 $OPENAI_API_KEY 或 $PRTHINKER_OPENAI_API_KEY
     # organization 可選

   anthropic:
     model: claude-opus-4-7
     base_url: https://api.anthropic.com
     version: "2023-06-01"
     # api_key 來自 $ANTHROPIC_API_KEY 或 $PRTHINKER_ANTHROPIC_API_KEY

   remote:
     url: https://my-inference-host:9000
     timeout_seconds: 600
     use_pipeline_endpoint: true   # 打 /review 而非每個 step 都打 /ask

哪些東西不會放在這
------------------

* **密鑰**\ ──如上述。
* ``GITHUB_TOKEN`` / ``GITHUB_REPOSITORY``\ ──由 Actions 或 shell 提供。
* ``--pr-number`` / ``--dry-run`` / ``--steps``\ ──per-invocation 而非
  per-repo。

驗證
----

Loader 是 Pydantic v2 model 且設 ``extra="forbid"``\ ：未知 key 會直接拋
validation error 而不是默默忽略。想做快速 schema check 可以跑
``prthinker review-file - --config .prthinker.yaml``\ （stdin 給空就好）。

提示
----

* ``.prthinker.yaml`` 建議 commit 進去，這樣 config 改動會出現在 PR
  review 裡，跟對應的程式改動一起被審。
* ``.prthinker/cache.sqlite`` 與 ``.prthinker/telemetry.sqlite`` 請放
  ``.gitignore``\ ──它們是執行時產生的 state、不是 config。
* 同一份 YAML 同時餵 runner（在你的 GHA workflow）跟 server 都行；如果是
  同一台機器 host 兩邊，指到同一份檔即可。
