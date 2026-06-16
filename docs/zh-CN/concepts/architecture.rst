架构
====

``prthinker`` 围绕着六个被 ``CLAUDE.md`` 明定为必须遵守的设计模式而组织。
每个扩展点都对应其中之一，加新 step、新 backend、新 retriever 都只是把
代码塞进现有缝隙──不会动到 pipeline。

一句话说明
----------

在谈设计模式之前，先给所有人一段话：当开发者提议一项代码变更
（一个 *Pull Request*）时，``prthinker`` 会像一位细心的资深工程师那样
审查它──总结这次改了什么、指出 bug 与风险点、把评论直接贴在受影响的
行上，其中许多还附带一键「应用此修复」按钮。它记得反馈（团队拒绝过的
评论不再重复；采纳过的建议会被当成示例重用），并且可以设成合并前的
必需 gate。

整个代码库分成**两个半边**：

* 轻量的 **runner**\ （``prthinker/`` 包）负责跟 GitHub 对话、组 prompt、
  回帖结果。它不需要 GPU──只靠 ``httpx`` 与 ``pydantic``。
* 较重的 **AI 大脑**\ （``codes/`` 树）──语言模型本身，加上它的训练与
  FastAPI 推理服务器。这部分需要 GPU，也可以改用 OpenAI 或 Anthropic
  之类的付费 API 取代。

仓库结构
--------

.. only:: html

   .. mermaid::

      graph TD
          GHA[".github/workflows<br/>自动审查每个 PR"] --> CLI

          subgraph RUNNER["prthinker/ &mdash; runner（轻量、免 GPU）"]
              direction TB
              CLI["CLI 与入口<br/>cli*.py"]
              PIPE["Pipeline 与步骤<br/>pipeline.py · steps.py · findings.py"]
              BACK["Backends &mdash; 可替换的 AI 大脑<br/>local · remote · OpenAI · Anthropic · Gemini…"]
              PLAT["Platforms &mdash; 代码平台<br/>GitHub · GitLab · Gitea"]
              CORP["记忆 / 语料<br/>accepted · dismissed · lessons · RAG · 知识图谱"]
              SIG["免模型导航信号<br/>orientation · bidi · 合并标记 · 残留 debug…"]
              EXT["研究级扩展（opt-in）<br/>personas · counterfactual · risk-score…"]
              OUT["报告与输出<br/>Markdown · HTML · SARIF · JUnit · Sonar · CSV"]
              SEC["安全<br/>redaction · injection guard · sandbox"]
              CLI --> PIPE
              PIPE --> BACK & PLAT & CORP & SIG & EXT & OUT & SEC
          end

          subgraph SERVER["codes/ &mdash; 训练与推理（重、需 GPU）"]
              direction TB
              FAST["FastAPI 推理服务器<br/>codes/run/fastapi_server.py"]
              PROMPT["Prompt 模板（真实来源）<br/>codes/run/CoT_Prompts/"]
              TRAIN["LoRA 微调<br/>codes/train/（Qwen3-Coder-30B…）"]
              UTIL["模型 + FAISS 工具<br/>codes/util/"]
          end

          BACK -. "HTTP /review · /ask" .-> FAST
          FAST --- PROMPT & UTIL
          TRAIN -. "产出模型" .-> FAST

.. only:: latex

   .. code-block:: text

      .github/workflows  ── 自动审查每个 PR，驱动 runner
      prthinker/         ── RUNNER（轻量、免 GPU）
        cli*.py            命令行入口
        pipeline / steps   一步步的审查引擎
        backends/          可替换的 AI 大脑（local · OpenAI · Anthropic · Gemini…）
        platforms/         代码平台（GitHub · GitLab · Gitea）
        corpora            记忆（accepted · dismissed · lessons · RAG · 知识图谱）
        signals            免模型导航信号 + 研究级扩展
        reports / safety   输出格式 + redaction / injection guard / sandbox
      codes/             ── AI 大脑（重、需 GPU）
        run/fastapi_server.py   runner 通过 HTTP 调用的推理服务器
        run/CoT_Prompts/        prompt 模板（单一真实来源）
        train/                  LoRA 微调（Qwen3-Coder-30B…）
        util/                   模型加载 + FAISS 检索

runner 通过两种 HTTP 形状（``/ask`` 与 ``/review``，详见下方
`Runner 与 server 的分工`_）连到大脑。支撑用的目录落在两个半边之外：
``docs/``（这个三语 Sphinx 站点）、``docker/``（一键自托管）、``datas/``
（RAG 规则文档、架构图、fixtures）、``paper/``（论文与幻灯片）与
``tests/``。

设计模式总览
------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - 模式
     - 对应实现
   * - Strategy
     - ``prthinker.backends.base.InferenceBackend`` 加上
       ``LocalHFBackend`` 与 ``RemoteHttpBackend`` 两个实现。
   * - Factory
     - ``prthinker.backends.create_backend(config)`` 是建造 backend 的
       唯一入口。耗资源的 import（torch、transformers）延后到 concrete
       backend 内部。
   * - Template Method
     - 每个 step 提供 ``build_prompt(ctx)``\ ；pipeline 用同一个循环跑过它们。
       Prompt 字符串住在 ``codes/run/CoT_Prompts/``\ ，通过 builder 取得──
       不会 inline 在执行路径。
   * - Registry
     - ``@register_step`` 把新的 ``ReviewStep`` subclass 追加到模块级别的
       列表。加 step 不需要动 ``pipeline.py``\ 。
   * - Repository
     - 所有 FAISS 操作都走 ``prthinker.rag.RAGRetriever`` 的实现。
       Embedding 模型只加载一次。
   * - Dependency Injection
     - Backend、retriever、filter、store 都当构造参数传给 ``CoTPipeline``\ 。
       Pipeline body 内不去抓 module-level singleton。

组件图
------

::

   ┌────────────────────────────────────────────────────────────┐
   │ prthinker/                                              │
   │                                                            │
   │  cli.py ────────────┐                                      │
   │                     ▼                                      │
   │  pipeline.CoTPipeline ─── backends.InferenceBackend ◀──┐   │
   │      │           │              │                     │   │
   │      │           │              ▼                     │   │
   │      │           │     LocalHFBackend       RemoteHttpBackend
   │      │           │            (GPU)        (HTTP /ask)      │
   │      │           ▼                                          │
   │      │     rag.RAGRetriever ◀── FaissRAGRetriever            │
   │      │                          NoOpRetriever                │
   │      │                          RemoteRAGRetriever (HTTP /rag) │
   │      │                                                       │
   │      ├── steps.ReviewStep registry                            │
   │      │     • first_summary    • code_smell                    │
   │      │     • first_code_review• total_summary                 │
   │      │     • linter           • inline_findings（per-file）   │
   │      │                                                       │
   │      ├── dismissed.DismissedFilter   （丢掉相似的重复命中）  │
   │      ├── accepted.AcceptedExamplesRetriever （top-K 示例）   │
   │      │                                                       │
   │      ▼                                                       │
   │  github_api / checks / ci_signals                             │
   │                                                              │
   └──────────────────────────────────────────────────────────────┘

           runner 端                      server 端
   ┌─────────────────────────┐         ┌─────────────────────────────────────────┐
   │ 薄：httpx + pydantic    │ ──HTTP──▶│ 重：torch、transformers、faiss、       │
   │ 不需要 GPU              │         │ FaissRAGRetriever、DismissedFilter、   │
   │                         │         │ AcceptedExamplesRetriever              │
   └─────────────────────────┘         └─────────────────────────────────────────┘

CLI 本身是一个小包：\ ``cli.py`` 只放入口与「名称 → handler」registry，
``cli_parser.py`` 建 argparse 树，\ ``cli_review.py`` / ``cli_commands.py``
则放各命令 handler。新增一个子命令只需一笔 registry 条目加一个 handler——
分派没有 ``if/elif`` 链。

Runner 与 server 的分工
-----------------------

Runner 刻意做得很薄──唯一必装的依赖只有 ``httpx`` 和 ``pydantic``\ 。完整
ML stack 与 FAISS index 都住在服务器端。这个分工就是为什么 GitHub Action
可以在默认的 GitHub-hosted runner（没有 GPU）上跑起来。

两种 HTTP 形状把它们接起来：

* ``/ask``\ ──单一 prompt 进、纯文本出。Runner 自己编排 pipeline 时用
  （\ ``--backend remote`` 但没开 ``--use-remote-pipeline``\ ）。
* ``/review``\ ──完整 diff 进、结构化 ``ReviewResponse`` 出。服务器跑 RAG +
  全部 step + dismissed filter，返回 parsed inline findings。内附 workflow
  默认用这个。

两个 endpoint 共用同一个在 server boot 时加载的 backend instance。

加新 step
---------

完整的新 step 住在单一文件内。Pipeline 通过 registry 自动拾起──不会动
``pipeline.py``\ 。

.. code-block:: python

   # prthinker/extras/security_audit.py
   from prthinker.steps import (
       ReviewContext, ReviewStep, register_step,
   )

   _PROMPT = """
   重新阅读以下 code diff，列出任何可能造成安全风险的输入处理。
   只返回 markdown bullet list、不要 prose。

   Diff:
   {code_diff}
   """

   @register_step
   class SecurityAuditStep(ReviewStep):
       name = "security_audit"

       def build_prompt(self, ctx: ReviewContext) -> str:
           return _PROMPT.format(code_diff=ctx.code_diff)

在 process 启动时 import 这个 module 一次（例如在
``prthinker/__init__.py``\ ），这样 ``@register_step`` decorator 才会跑。
新的 step 就会出现在 ``prthinker review-file --steps`` 里，默认的
``--steps ""``\ （全部注册的）也会把它跑进去。

加新 backend
------------

继承 ``InferenceBackend``\ ，把构造路径加到 ``create_backend``\ 。Pipeline 不需要
动。
