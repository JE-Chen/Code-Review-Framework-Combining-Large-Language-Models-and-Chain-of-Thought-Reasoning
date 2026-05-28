架構
====

``prthinker`` 圍繞著六個被 ``CLAUDE.md`` 明訂為必須遵守的設計模式而組織。
每個擴充點都對應其中之一，加新 step、新 backend、新 retriever 都只是把
程式碼塞進現有縫隙──不會動到 pipeline。

設計模式總覽
------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - 模式
     - 對應實作
   * - Strategy
     - ``prthinker.backends.base.InferenceBackend`` 加上
       ``LocalQwen3Backend`` 與 ``RemoteHttpBackend`` 兩個實作。
   * - Factory
     - ``prthinker.backends.create_backend(config)`` 是建造 backend 的
       唯一入口。耗資源的 import（torch、transformers）延後到 concrete
       backend 內部。
   * - Template Method
     - 每個 step 提供 ``build_prompt(ctx)``\ ；pipeline 用同一個迴圈跑過它們。
       Prompt 字串住在 ``codes/run/CoT_Prompts/``\ ，透過 builder 取得──
       不會 inline 在執行路徑。
   * - Registry
     - ``@register_step`` 把新的 ``ReviewStep`` subclass 追加到模組層級的
       清單。加 step 不需要動 ``pipeline.py``\ 。
   * - Repository
     - 所有 FAISS 操作都走 ``prthinker.rag.RAGRetriever`` 的實作。
       Embedding 模型只載一次。
   * - Dependency Injection
     - Backend、retriever、filter、store 都當建構參數傳給 ``CoTPipeline``\ 。
       Pipeline body 內不去抓 module-level singleton。

元件圖
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
   │      │     • linter           • inline_findings（per-file）  │
   │      │                                                       │
   │      ├── dismissed.DismissedFilter   （丟掉相似的重複命中） │
   │      ├── accepted.AcceptedExamplesRetriever （top-K 範例）   │
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

Runner 與 server 的分工
-----------------------

Runner 刻意做得很薄──唯一必裝的相依只有 ``httpx`` 和 ``pydantic``\ 。完整
ML stack 與 FAISS index 都住在伺服器端。這個分工就是為什麼 GitHub Action
可以在預設的 GitHub-hosted runner（沒有 GPU）上跑起來。

兩種 HTTP 形狀把它們接起來：

* ``/ask``\ ──單一 prompt 進、純文字出。Runner 自己編排 pipeline 時用
  （\ ``--backend remote`` 但沒開 ``--use-remote-pipeline``\ ）。
* ``/review``\ ──完整 diff 進、結構化 ``ReviewResponse`` 出。伺服器跑 RAG +
  全部 step + dismissed filter，回傳 parsed inline findings。內附 workflow
  預設用這個。

兩個 endpoint 共用同一個在 server boot 時載入的 backend instance。

加新 step
---------

完整的新 step 住在單一檔案內。Pipeline 透過 registry 自動撿起來──不會動
``pipeline.py``\ 。

.. code-block:: python

   # prthinker/extras/security_audit.py
   from prthinker.steps import (
       ReviewContext, ReviewStep, register_step,
   )

   _PROMPT = """
   重新閱讀以下 code diff，列出任何可能造成安全風險的輸入處理。
   只回傳 markdown bullet list、不要 prose。

   Diff:
   {code_diff}
   """

   @register_step
   class SecurityAuditStep(ReviewStep):
       name = "security_audit"

       def build_prompt(self, ctx: ReviewContext) -> str:
           return _PROMPT.format(code_diff=ctx.code_diff)

在 process 啟動時 import 這個 module 一次（例如在
``prthinker/__init__.py``\ ），這樣 ``@register_step`` decorator 才會跑。
新的 step 就會出現在 ``prthinker review-file --steps`` 裡，預設的
``--steps ""``\ （全部註冊的）也會把它跑進去。

加新 backend
------------

繼承 ``InferenceBackend``\ ，把建構路徑加到 ``create_backend``\ 。Pipeline 不需要
動。
