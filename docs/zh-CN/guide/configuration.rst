配置
====

每个 CLI flag 都有对应的环境变量。CLI 参数优先于环境变量，环境变量优先于
包默认。配置在启动时就会校验──不合法的组合直接抛异常，不会偷偷退化。

Backend 选择
------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - 环境变量
     - 默认
   * - ``--backend {local,remote,openai,anthropic,gemini,cohere,mistral,claude-cli,codex-cli}``
     - ``PRTHINKER_BACKEND``
     - ``remote``
   * - ``--remote-url URL``
     - ``PRTHINKER_REMOTE_URL``
     - *(remote 时必填)*
   * - ``--remote-api-key TOKEN``
     - ``PRTHINKER_REMOTE_API_KEY``
     - *(未设)*
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
     - *(未设)*

``--use-remote-pipeline`` 每个文件只调用一次 ``/review``\ ，而不是 runner 上
循环打 ``/ask``\ 。这样比较快、且把 prompt 编排集中在服务器，缺点是绑住
runner 必须对应有 ``/review`` endpoint 的服务器版本。

OpenAI 兼容提供方（\ ``--backend openai``\ ）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

这一个 backend 对接任何实现 OpenAI ``POST /chat/completions`` 形状的
服务──OpenAI 本家、Azure OpenAI、vLLM、Ollama（\ ``/v1``\ ）、LM Studio、
llama.cpp server、Together AI、Groq、DeepInfra、OpenRouter ……

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - 环境变量
     - 默认
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
     - *(未设)*

Anthropic Claude（\ ``--backend anthropic``\ ）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - 环境变量
     - 默认
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

本机 agent CLI（\ ``--backend claude-cli``\ ）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

以非交互 print 模式（\ ``claude -p``\ ）运行本机安装的 ``claude`` CLI，
每次生成起一个子进程。Prompt 走 stdin 传入──评审 prompt 内嵌整份 diff，
作为命令行参数会撞上 Windows 的长度上限──响应则要求
``--output-format json``\ ，让结果文本与 token 用量能确定性解析
（纯文本输出会原样退回）。

与 HTTP backend 不同，CLI 可通过 ``--claude-cli-allowed-tools``
（转发为 ``--allowedTools``\ ）获得工具集，让评审能以完整的本机工具链
查阅工作树──读文件、grep、追 import──而不是只看 prompt 文本。
``--claude-cli-workdir`` 界定工具作用的目录。

.. list-table::
   :header-rows: 1
   :widths: 38 34 28

   * - CLI flag
     - 环境变量
     - 默认
   * - ``--claude-cli-path PATH``
     - ``PRTHINKER_CLAUDE_CLI_PATH``
     - ``claude``
   * - ``--claude-cli-model NAME``
     - ``PRTHINKER_CLAUDE_CLI_MODEL``
     - *(CLI 自身默认)*
   * - ``--claude-cli-workdir PATH``
     - ``PRTHINKER_CLAUDE_CLI_WORKDIR``
     - ``.``
   * - ``--claude-cli-allowed-tools LIST``
     - ``PRTHINKER_CLAUDE_CLI_ALLOWED_TOOLS``
     - *(未设──沿用 CLI 自身工具策略)*
   * - ``--claude-cli-timeout SECONDS``
     - ``PRTHINKER_CLAUDE_CLI_TIMEOUT``
     - ``3600``

本机 agent CLI（\ ``--backend codex-cli``\ ）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

以 headless 模式运行本机安装的 ``codex`` CLI（\ ``codex exec --json
--skip-git-repo-check -C <workdir> -``\ ），每次生成起一个子进程。
Prompt 走 stdin 传入（结尾的 ``-``\ ）；输出为 NDJSON，最后一个
``agent_message`` 事件即为答案，token 用量取自 ``turn.completed``\ 。

Sandbox 模式默认 ``read-only``\ ：CLI 可用自身工具链读取工作树，但
绝不改动它。受信任的环境可改用 ``workspace-write`` 或
``danger-full-access``\ 。

.. list-table::
   :header-rows: 1
   :widths: 38 34 28

   * - CLI flag
     - 环境变量
     - 默认
   * - ``--codex-cli-path PATH``
     - ``PRTHINKER_CODEX_CLI_PATH``
     - ``codex``
   * - ``--codex-cli-model NAME``
     - ``PRTHINKER_CODEX_CLI_MODEL``
     - *(CLI 自身默认)*
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

默认关闭。开启 ``--arbitration`` 后，``--arbitration-backends`` 列出的
每个 backend 会重新评判主模型的 inline findings：每个仲裁者收到
findings 清单加 diff，逐条投 ``confirm`` / ``reject``\ ，再由策略合并
票数──被否决的 finding 在发布前就被剔除。

每个仲裁者沿用它作为主 backend 时的同一组 flags / 环境变量
（\ ``openai`` 仲裁者读 ``--openai-*``\ ，``claude-cli`` 仲裁者读
``--claude-cli-*``\ ，依此类推）。

这一层采用 fail-open：仲裁者出错或输出不可解析视为弃权，没有任何有效
票的 finding 一律保留。仲裁只会删噪音──不会因仲裁者不稳而丢失 finding。

.. list-table::
   :header-rows: 1
   :widths: 42 34 24

   * - CLI flag
     - 环境变量
     - 默认
   * - ``--arbitration``
     - ``PRTHINKER_ARBITRATION``
     - ``false``
   * - ``--arbitration-backends a,b``
     - ``PRTHINKER_ARBITRATION_BACKENDS``
     - *(未设)*
   * - ``--arbitration-strategy {majority,unanimous,any}``
     - ``PRTHINKER_ARBITRATION_STRATEGY``
     - ``majority``
   * - ``--arbitration-max-new-tokens N``
     - ``PRTHINKER_ARBITRATION_MAX_NEW_TOKENS``
     - ``4096``

``majority`` 只有 reject 多于 confirm 才剔除（平票保留），
``unanimous`` 只要有一票 reject 就剔除，``any`` 只要有一票 confirm
就保留。

由两个本机 agent CLI 组成仲裁小组的多模型评审
（完整脚本见 ``examples/multi-model-review.sh``\ ）：

.. code-block:: bash

   prthinker review-pr \
       --repo owner/name --pr-number 42 \
       --per-file --inline-review \
       --arbitration \
       --arbitration-backends claude-cli,codex-cli \
       --arbitration-strategy majority

RAG 与规则
----------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - 环境变量
     - 默认
   * - ``--no-rag``
     - ``PRTHINKER_RAG_ENABLED=false``
     - RAG 开启
   * - ``--remote-rag``
     - ``PRTHINKER_REMOTE_RAG``
     - ``false``
   * - ``--rag-threshold FLOAT``
     - ``PRTHINKER_RAG_THRESHOLD``
     - ``0.7``
   * - ``--rules-dir PATH``
     - ``PRTHINKER_RULES_DIR``
     - *(未设)*

``--remote-rag`` 让 runner 调用服务器的 ``/rag``\ ，不在本地加载 4B embedding
模型──默认的 GitHub-hosted runner 必须开这个。

``--rules-dir`` 会把指定目录下的每个 ``*.md`` 都视为一条常驻团队规则，
排在 RAG 检索出来的规则之后。

逐文件模式与 inline review
--------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - CLI flag
     - 环境变量
     - 默认
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
     - *(未设)*
   * - ``--target-file PATH``
     - ``PRTHINKER_TARGET_FILE``
     - *(未设)*

Inline review 需要先启用 per-file 模式（inline-findings step 需要知道
正在审哪个文件）。光开 ``--inline-review`` 而没有 ``--per-file`` 不会坏，
只是没效果。

``--exclude-globs`` 是逗号分隔之 fnmatch patterns（例如
``.idea/*,datas/*,*.md,*.lock``\ ）。parse 出的 diff 中匹配任一
pattern 之 path 在 per-file loop 前就被丢掉──IDE state、生成
数据、大段文档变更等不浪费 GPU 时间。

``--target-file`` 把 per-file loop 限定在单一精确 path。搭
``--output-json`` 让 CI matrix shard 各自接管一个 file 之 review
（matrix workflow 见 :doc:`github-actions`\ ）。

Matrix 分片与 aggregation
-------------------------

对于把 per-file review 切到多 runner 之 workflow（CI matrix 或外
部 job queue），每个 shard 跑 ``review-pr`` 之 *partial* 模式，最
后一个 aggregator 把所有 shard 之 findings 合一成单一 PR-level
review。

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - CLI flag
     - 环境变量
     - 默认
   * - ``--output-json PATH``
     - ``PRTHINKER_OUTPUT_JSON``
     - *(未设)*
   * - ``--aggregate-from DIR``
     - ``PRTHINKER_AGGREGATE_FROM``
     - *(未设)*

``--output-json`` 让 ``review-pr`` 从「post 到 GitHub」改为「把
partial ``ReviewResult`` 序列化到磁盘」。Shard 仍正常跑 pipeline
但**不**做 summary comment upsert、inline review submit、gate
open，这些交给 ``aggregate`` 子指令──它读 ``--aggregate-from``
下所有 JSON 后合一 post。

合并前 gate
-----------

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - CLI flag
     - 环境变量
     - 默认
   * - ``--gate-on {none,warning,error}``
     - ``PRTHINKER_GATE_ON``
     - ``none``

详见 :doc:`../concepts/ci-and-gate`。设为 ``none`` 为纯建议模式，设为
``error`` 则只要有 error 严重度的 finding 就让 Check Run failure。

CI 信号
-------

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - CLI flag
     - 环境变量
     - 默认
   * - ``--include-ci-signals``
     - ``PRTHINKER_INCLUDE_CI_SIGNALS``
     - ``false``
   * - ``--ci-signal-max-jobs N``
     - ``PRTHINKER_CI_SIGNAL_MAX_JOBS``
     - ``5``
   * - ``--ci-signal-tail-chars N``
     - ``PRTHINKER_CI_SIGNAL_TAIL_CHARS``
     - ``4000``

信号通过 platform adapter 获取：GitHub 读失败的 Actions job log，
GitLab 读失败 pipeline job 的 trace。没有 CI API 的平台会记一行 log
后跳过。

服务器端
--------

这些变量是由 ``codes/run/fastapi_server.py`` 在启动时读取的，\ **不是** runner
CLI 在读。

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - 环境变量
     - 效果
   * - ``PRTHINKER_DISMISSED_PATH``
     - ``dismissed.jsonl`` 路径。未设 / 不存在 → 过滤器关闭。
   * - ``PRTHINKER_DISMISSED_THRESHOLD``
     - 丢弃重复命中所用的 cosine similarity 下限。默认 ``0.85``\ 。
   * - ``PRTHINKER_ACCEPTED_PATH``
     - ``accepted.jsonl`` 路径。未设 / 不存在 → 不注入示例。
   * - ``PRTHINKER_ACCEPTED_THRESHOLD``
     - 采纳为 top-K 示例的 cosine 下限。默认 ``0.6``\ 。
   * - ``PRTHINKER_ACCEPTED_TOP_K``
     - 注入几条示例。默认 ``3``\ 。
   * - ``PRTHINKER_MAX_JOBS``
     - 异步 job 表（review 与 ask 各一张）的上限；先淘汰已终止的
       job，当所有 slot 都被进行中的 job 占满时，submit 端点返回
       ``503``\ 。默认 ``32``\ 。
   * - ``PRTHINKER_MAX_INPUT_TOKENS``
     - prompt 超过此 token 预算即在边界直接拒绝，而不是审查中途
       CUDA OOM。默认 ``16384``\ 。
   * - ``PRTHINKER_MAX_NEW_TOKENS``
     - 服务器端生成长度上限；wire schema 会把 ``max_new_tokens``
       clamp 到相同范围。默认 ``32768``\ 。

输出与 logging
--------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - 环境变量
     - 默认
   * - ``--log-level LEVEL``
     - ``PRTHINKER_LOG_LEVEL``
     - ``INFO``
   * - ``--steps a,b,c``
     - *(无)*
     - *(全部注册的 step)*
   * - ``--max-new-tokens N``
     - ``PRTHINKER_MAX_NEW_TOKENS``
     - ``32768``
   * - ``--output-dir PATH``
     - *(只在 review-file)*
     - *(无)*
