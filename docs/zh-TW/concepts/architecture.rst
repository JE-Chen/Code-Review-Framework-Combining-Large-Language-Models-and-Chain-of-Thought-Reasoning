架構
====

``prthinker`` 圍繞著六個被 ``CLAUDE.md`` 明訂為必須遵守的設計模式而組織。
每個擴充點都對應其中之一，加新 step、新 backend、新 retriever 都只是把
程式碼塞進現有縫隙──不會動到 pipeline。

一句話說明
----------

在談設計模式之前，先給所有人一段話：當開發者提議一項程式碼變更
（一個 *Pull Request*）時，``prthinker`` 會像一位細心的資深工程師那樣
審查它──摘要這次改了什麼、指出 bug 與風險點、把留言直接貼在受影響的
行上，其中許多還附帶一鍵「套用此修正」按鈕。它記得回饋（團隊拒絕過的
留言不再重複；採納過的建議會被當成範例重用），並且可以設成合併前的
必要 gate。

整個程式碼庫分成**兩個半邊**：

* 輕量的 **runner**\ （``prthinker/`` 套件）負責跟 GitHub 對話、組 prompt、
  回貼結果。它不需要 GPU──只靠 ``httpx`` 與 ``pydantic``。
* 較重的 **AI 大腦**\ （``codes/`` 樹）──語言模型本身，加上它的訓練與
  FastAPI 推論伺服器。這部分需要 GPU，也可以改用 OpenAI 或 Anthropic
  之類的付費 API 取代。

專案結構
--------

.. only:: html

   .. mermaid::

      graph TD
          GHA[".github/workflows<br/>自動審查每個 PR"] --> CLI

          subgraph RUNNER["prthinker/ &mdash; runner（輕量、免 GPU）"]
              direction TB
              CLI["CLI 與進入點<br/>cli*.py"]
              PIPE["Pipeline 與步驟<br/>pipeline.py · steps.py · findings.py"]
              BACK["Backends &mdash; 可替換的 AI 大腦<br/>local · remote · OpenAI · Anthropic · Gemini…"]
              PLAT["Platforms &mdash; 程式碼平台<br/>GitHub · GitLab · Gitea"]
              CORP["記憶 / 語料<br/>accepted · dismissed · lessons · RAG · 知識圖譜"]
              SIG["免模型導航訊號<br/>orientation · bidi · 合併標記 · 殘留 debug…"]
              EXT["研究級擴充（opt-in）<br/>personas · counterfactual · risk-score…"]
              OUT["報告與輸出<br/>Markdown · HTML · SARIF · JUnit · Sonar · CSV"]
              SEC["安全<br/>redaction · injection guard · sandbox"]
              CLI --> PIPE
              PIPE --> BACK & PLAT & CORP & SIG & EXT & OUT & SEC
          end

          subgraph SERVER["codes/ &mdash; 訓練與推論（重、需 GPU）"]
              direction TB
              FAST["FastAPI 推論伺服器<br/>codes/run/fastapi_server.py"]
              PROMPT["Prompt 模板（真實來源）<br/>codes/run/CoT_Prompts/"]
              TRAIN["LoRA 微調<br/>codes/train/（Qwen3-Coder-30B…）"]
              UTIL["模型 + FAISS 工具<br/>codes/util/"]
          end

          BACK -. "HTTP /review · /ask" .-> FAST
          FAST --- PROMPT & UTIL
          TRAIN -. "產出模型" .-> FAST

.. only:: latex

   .. code-block:: text

      .github/workflows  ── 自動審查每個 PR，驅動 runner
      prthinker/         ── RUNNER（輕量、免 GPU）
        cli*.py            命令列進入點
        pipeline / steps   一步步的審查引擎
        backends/          可替換的 AI 大腦（local · OpenAI · Anthropic · Gemini…）
        platforms/         程式碼平台（GitHub · GitLab · Gitea）
        corpora            記憶（accepted · dismissed · lessons · RAG · 知識圖譜）
        signals            免模型導航訊號 + 研究級擴充
        reports / safety   輸出格式 + redaction / injection guard / sandbox
      codes/             ── AI 大腦（重、需 GPU）
        run/fastapi_server.py   runner 透過 HTTP 呼叫的推論伺服器
        run/CoT_Prompts/        prompt 模板（單一真實來源）
        train/                  LoRA 微調（Qwen3-Coder-30B…）
        util/                   模型載入 + FAISS 檢索

runner 透過兩種 HTTP 形狀（``/ask`` 與 ``/review``，詳見下方
`Runner 與 server 的分工`_）連到大腦。支援用的目錄落在兩個半邊之外：``docs/``
（這個三語 Sphinx 站點）、``docker/``（一鍵自架）、``datas/``（RAG 規則
文件、架構圖、fixtures）、``paper/``（論文與投影片）與 ``tests/``。

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

CLI 本身是一個小套件：\ ``cli.py`` 只放進入點與「名稱 → handler」registry，
``cli_parser.py`` 建 argparse 樹，\ ``cli_review.py`` / ``cli_commands.py``
則放各指令 handler。新增一個子指令只需一筆 registry 條目加一個 handler——
分派沒有 ``if/elif`` 鏈。

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
