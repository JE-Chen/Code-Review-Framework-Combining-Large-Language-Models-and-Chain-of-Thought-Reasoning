架构
====

``reviewmind`` 围绕着六个被 ``CLAUDE.md`` 明定为必须遵守的设计模式而组织。
每个扩展点都对应其中之一，加新 step、新 backend、新 retriever 都只是把
代码塞进现有缝隙──不会动到 pipeline。

设计模式总览
------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - 模式
     - 对应实现
   * - Strategy
     - ``reviewmind.backends.base.InferenceBackend`` 加上
       ``LocalQwen3Backend`` 与 ``RemoteHttpBackend`` 两个实现。
   * - Factory
     - ``reviewmind.backends.create_backend(config)`` 是建造 backend 的
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
     - 所有 FAISS 操作都走 ``reviewmind.rag.RAGRetriever`` 的实现。
       Embedding 模型只加载一次。
   * - Dependency Injection
     - Backend、retriever、filter、store 都当构造参数传给 ``CoTPipeline``\ 。
       Pipeline body 内不去抓 module-level singleton。

组件图
------

::

   ┌────────────────────────────────────────────────────────────┐
   │ reviewmind/                                              │
   │                                                            │
   │  cli.py ────────────┐                                      │
   │                     ▼                                      │
   │  pipeline.CoTPipeline ─── backends.InferenceBackend ◀──┐   │
   │      │           │              │                     │   │
   │      │           │              ▼                     │   │
   │      │           │     LocalQwen3Backend   RemoteHttpBackend
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

   # reviewmind/extras/security_audit.py
   from reviewmind.steps import (
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
``reviewmind/__init__.py``\ ），这样 ``@register_step`` decorator 才会跑。
新的 step 就会出现在 ``reviewmind review-file --steps`` 里，默认的
``--steps ""``\ （全部注册的）也会把它跑进去。

加新 backend
------------

继承 ``InferenceBackend``\ ，把构造路径加到 ``create_backend``\ 。Pipeline 不需要
动。
