Secret 过滤与 MCP 集成
======================

两个彼此无关的扩展，但共享同一个动机：让 prthinker 在原本的 GHA workflow
之外也安全、便利。

Secret redaction（\ ``--redact-secrets``\ ）
--------------------------------------------

Backend 接到付费第三方 API（OpenAI、Anthropic …）时，PR diff 内可能夹带
被 ``.gitignore`` 漏掉的真实 secret──diff 显示出 ``.env`` 内容、test
fixture 写死的 token、snapshot test 内的 JWT。开 ``--redact-secrets``
（env ``PRTHINKER_REDACT_SECRETS=true``\ ）后，runner 会在送出任何 backend
call 前对 diff 做 pre-pass，把已知的 secret pattern 换成
``<REDACTED:<kind>>``\ 。

覆盖的 pattern
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - kind
     - 对应
   * - ``private-key``
     - PEM ``-----BEGIN ... PRIVATE KEY-----`` 整块
   * - ``github-token``
     - ``ghp_`` / ``gho_`` / ``ghu_`` / ``ghs_`` / ``ghr_`` PAT
   * - ``anthropic-key``
     - ``sk-ant-…``
   * - ``openai-key``
     - ``sk-…`` 与 ``sk-proj-…``\ （排除 Anthropic 前缀）
   * - ``stripe-key``
     - ``sk_live_…`` / ``sk_test_…`` / ``rk_live_…`` / ``rk_test_…``
   * - ``aws-access-key-id``
     - ``AKIA`` / ``ASIA`` / ``AIDA`` / ``AROA`` / ``AGPA`` / ``ANPA`` / ``ANVA``
   * - ``slack-token``
     - ``xoxa-`` / ``xoxb-`` / ``xoxp-`` / ``xoxr-`` / ``xoxs-``
   * - ``gcp-api-key``
     - ``AIza…``\ （39 字符）
   * - ``twilio-sid``
     - ``AC`` 加 32 个 hex
   * - ``jwt``
     - 三段 base64url 用 ``.`` 串接，header 起头 ``eyJ``

检测规则刻意保守──code review 出现误判是噪声但可修；漏判则是 secret 真的
泄漏出去。

设计性质
~~~~~~~~

* **Idempotent。**\ 已 redacted 过的 diff 再喂一次是 no-op──
  ``<REDACTED:...>`` 不会被自己当成 secret。
* **对 cache 友好。**\ Redaction 在 prompt 组装与 cache key 计算之前跑，
  所以同一个 PR 跑两次仍然能命中同一份 cache，不管有没有 secret 被换掉。
* **会 log、不会泄漏。**\ ``RedactionReport`` 只统计各 kind 的命中次数，
  从不包含内容，CI log 上线安全。

什么时候不要开
~~~~~~~~~~~~~~

* Backend 是本地 HF backend 或自部署 FastAPI（与 repo 同网段）时，redaction
  只有形式上的意义──secret 并没有要去哪。关掉可以让 diff 看起来原样。
* 接付费第三方 backend 时，请当成必选。

Model Context Protocol 集成
---------------------------

Model Context Protocol（MCP）是让 LLM client（Claude Desktop、Cursor、
Continue、Cline、Zed …）调用外部 tool 的开放标准。prthinker 内附一个
MCP server 适配器，任何 MCP client 都能在 IDE 内直接驱动 review──不必
通过 GHA。

安装
~~~~

.. code-block:: bash

   pip install -e ".[mcp]"

这会在 runner extras 之上多装 ``mcp`` SDK。

暴露的 tool
~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - tool name
     - 做什么
   * - ``review_diff``
     - 对 unified diff 字符串跑完整 CoT pipeline，返回与 PR 评论一样的
       markdown body。\ ``redact_secrets`` 默认 ``True``\ 。
   * - ``triage_diff``
     - 对 unified diff 字符串跑无需模型的静态信号（不调用 backend）：冲突标记、
       Trojan-Source 字符、吞错、重命名、删除、mode 变更、大段粘贴、纯格式
       变更、覆盖缺口、残留 debug 与延迟工作标记。瞬间且免费;\
       ``redact_secrets`` 默认 ``True``\ 。输出同 ``triage`` CLI 命令\ 。
   * - ``stats``
     - 对本地 telemetry SQLite 在指定时间区间做聚合，返回 markdown 表。
       适合「这周 review 烧了多少」这类提问。

配置
~~~~

Backend 选择用同一组 ``PRTHINKER_*`` env var；密钥只在 env，不会落到
MCP server 自己的 config 内。

Claude Desktop 配置示例（macOS 路径：
``~/Library/Application Support/Claude/claude_desktop_config.json``\ ）：

.. code-block:: json

   {
     "mcpServers": {
       "prthinker": {
         "command": "prthinker",
         "args": ["mcp"],
         "env": {
           "PRTHINKER_BACKEND": "anthropic",
           "ANTHROPIC_API_KEY": "sk-ant-...",
           "PRTHINKER_ANTHROPIC_MODEL": "claude-sonnet-4-6",
           "PRTHINKER_CACHE_ENABLED": "true",
           "PRTHINKER_TELEMETRY_ENABLED": "true"
         }
       }
     }
   }

同样的格式套到 Cursor、Continue、Cline、Zed 也行──请参考各 client 的
MCP 文档确认文件路径。

典型 IDE 流程
~~~~~~~~~~~~~

1. 本地 stage 改动：\ ``git add -p``\ 。
2. 在 IDE 聊天窗口：\ *「Run prthinker on my staged diff」*\ 。
3. Client 的 LLM 调用 ``review_diff``\ ，参数是 ``$(git diff --cached)``\ 。
4. Markdown review 流式回 chat panel；用户直接决定要不要采纳建议。

这对不想为了拿 review 而走完 PR + GHA 的个人开发者是 killer feature。

权衡
~~~~

* MCP 模式默认关掉 RAG（用 ``NoOpRetriever``\ ）。在 stdio 子进程内加载
  FAISS 太重、embedding 模型也很少装在用户笔记本──需要 RAG 时请改用
  ``PRTHINKER_BACKEND=remote`` 让 FastAPI server 负责检索。
* MCP server 在跨调用间是 stateless 的；cache 与 telemetry store 跨调用
  仍持久存在，所以 cost visibility 一样有效。
