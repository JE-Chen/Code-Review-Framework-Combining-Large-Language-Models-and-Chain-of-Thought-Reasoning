Repo 级配置
===========

把 ``.prthinker.yaml`` 放在 repo 根目录，可以集中管理所有非密钥类设置。
CLI 每次启动会自动读取，作为环境变量与 CLI flag 之下的默认层。

解析顺序（越下面越优先）
------------------------

1. 包内置默认。
2. 当前目录的 ``.prthinker.yaml``\ （或 ``--config PATH``\ ）。
3. 环境变量（\ ``PRTHINKER_*``\ 、\ ``OPENAI_API_KEY``\ ……）。
4. 命令行 flag。

**密钥绝不放 YAML。** API key、token、GitHub token 一律只从环境变量读取，
这样 commit 进 git 的 config 文件不会泄露 credential。

Schema
------

.. code-block:: yaml

   # .prthinker.yaml — 把所有开关都打开的示例
   backend: openai                # local | remote | openai | anthropic
   max_new_tokens: 8192

   per_file: true
   inline_review: true
   max_findings_per_file: 10

   rag:
     enabled: true
     threshold: 0.7
     rules_dir: ./team-rules      # 可选；*.md 文件变成团队规则
     remote: false                # 改打服务器 /rag、不在本地加载 FAISS

   gate:
     severity: error              # none | warning | error
                                  # 注意：用 'severity' 而非 'on'，
                                  # YAML 1.1 会把 `on` 解析为 boolean True。

   ci_signals:
     enabled: true
     max_jobs: 5
     tail_chars: 4000

   cache:
     enabled: true
     path: .prthinker/cache.sqlite
     ttl_days: 7                  # 设为 null 关掉 TTL

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
     # api_key 来自 $OPENAI_API_KEY 或 $PRTHINKER_OPENAI_API_KEY
     # organization 可选

   anthropic:
     model: claude-opus-4-7
     base_url: https://api.anthropic.com
     version: "2023-06-01"
     # api_key 来自 $ANTHROPIC_API_KEY 或 $PRTHINKER_ANTHROPIC_API_KEY

   remote:
     url: https://my-inference-host:9000
     timeout_seconds: 600
     use_pipeline_endpoint: true   # 打 /review 而非每个 step 都打 /ask

哪些东西不会放在这
------------------

* **密钥**\ ──如上述。
* ``GITHUB_TOKEN`` / ``GITHUB_REPOSITORY``\ ──由 Actions 或 shell 提供。
* ``--pr-number`` / ``--dry-run`` / ``--steps``\ ──per-invocation 而非
  per-repo。

校验
----

Loader 是 Pydantic v2 model 且设 ``extra="forbid"``\ ：未知 key 会直接抛
validation error 而不是默默忽略。想做快速 schema check 可以跑
``prthinker review-file - --config .prthinker.yaml``\ （stdin 给空就好）。

提示
----

* ``.prthinker.yaml`` 建议 commit 进去，这样 config 改动会出现在 PR
  review 里，跟对应的代码改动一起被审。
* ``.prthinker/cache.sqlite`` 与 ``.prthinker/telemetry.sqlite`` 请放
  ``.gitignore``\ ──它们是运行时产生的 state、不是 config。
* 同一份 YAML 同时喂 runner（在你的 GHA workflow）跟 server 都行；如果是
  同一台机器 host 两边，指到同一份文件即可。
