RAG 與規則包
============

Reviewer 的 prompt 留了一個專門放 *規則* 的槽位，會合併兩種來源：全域檢索
出的 best-practice rules（RAG）與 repo 自帶的常駐團隊規則。

全域 RAG
--------

``codes/util/faiss_util.py`` 用 ``Qwen/Qwen3-Embedding-4B`` 對
``datas/RAG_data/rag_data.py`` 中的 ``rule_docs`` 建立 ``IndexFlatIP``
（L2-normalised 向量）。Index 只在 module import 時建一次──查詢成本低。

Retriever 介面位於 ``prthinker.rag.RAGRetriever``\ 。提供三個實作：

* ``FaissRAGRetriever``\ ──in-process 包住 FAISS index。需要載入 embedding
  模型（約 8 GB VRAM）。用在推論伺服器端。
* ``RemoteRAGRetriever``\ ──POST 到伺服器的 ``/rag`` endpoint。讓薄 runner
  不必綁 embedding 模型。GitHub Action 用這個。
* ``NoOpRetriever``\ ──回 ``[]``\ 。做 pure-LLM baseline ablation 時用得到。

Threshold
~~~~~~~~~

``--rag-threshold``\ （預設 ``0.7``\ ）會丟掉與 query cosine 低於此值的文件。
這個旋鈕影響最大──太低 prompt 會塞一堆不相關規則；太高就餓死模型。

Per-repo 規則包
---------------

``--rules-dir`` flag（環境變數 ``PRTHINKER_RULES_DIR``\ ）會遞迴讀取目錄下所有
``*.md``\ （依路徑排序），把每個檔案的內容當成一條規則，\ **接在 RAG 檢索出
的規則後面**\ 注入 prompt。

與 RAG 規則有兩個重要差異：

* **常駐**\ ──不做相似度過濾。團隊已經把它 check 進 repo 表示「就是要適用」，
  所以一律帶上。
* **一檔一條**\ ──讓 git diff 容易稽核。

目錄結構範例::

   ./team-rules/
   ├── 010-imports.md
   ├── 020-error-handling.md
   ├── 030-logging.md
   └── 040-database.md

每檔應該是一則簡短易讀的規則：

.. code-block:: markdown

   # 資料庫查詢

   - 一律使用 parameterised query，不要用 f-string 拼 SQL。
   - 多句交易要用 `with conn:` 包起來。
   - 動 `users` table 的查詢必須帶 `WHERE user_id = ?` 條件，否則拒絕。

規則怎麼進到 prompt
-------------------

規則槽的唯一真實來源是 ``codes/run/CoT_Prompts/global_rule.py``\ 。Pipeline
呼叫 ``build_global_rule_template(prompt=..., rag_rules=merged_list)``\ ，
而 ``merged_list`` 是 *RAG 檢索出的規則* + *--rules-dir 規則* 的串接。

兩種規則都會渲染進 prompt 的
*"8. RAG Rules (Retrieval-Augmented Guidance)"* 區段。

接線圖
------

::

           --rules-dir
                │
                ▼
        load_rules_dir(path)
                │
                │  list[str]
                ▼
           extra_rules ──┐
                         │
   retriever.retrieve()  │
        │                ▼
        │       CoTPipeline._merge_rules()
        │                │
        ▼                ▼
   rag_docs ─── rag_docs (merged) ──▶ build_global_rule_template(...)
                                            │
                                            ▼
                                       backend.generate()

加新 retriever
--------------

繼承 ``RAGRetriever``\ ：

.. code-block:: python

   from prthinker.rag import RAGRetriever

   class HybridRetriever(RAGRetriever):
       """同時回 BM25 + FAISS 結果並去重。"""

       def __init__(self, bm25, faiss):
           self._bm25 = bm25
           self._faiss = faiss

       def retrieve(self, prompt: str) -> list[str]:
           seen: set[str] = set()
           out: list[str] = []
           for doc in self._bm25.search(prompt) + self._faiss.search(prompt):
               if doc not in seen:
                   seen.add(doc)
                   out.append(doc)
           return out

Pipeline 對 retriever 的唯一契約就是 ``retrieve(str) -> list[str]`` 這個
方法──沒有 global side effect、不要求 setup 順序。

Repository-context 檢索策略
---------------------------

在規則槽之外，逐檔審查 prompt 還可以前置從本機 work-tree
（``--repo-context-workdir``）檢索出的跨檔\ *repository context*\ 。
``--repo-context-strategy``\ （環境變數
``PRTHINKER_REPO_CONTEXT_STRATEGY``\ ，預設 ``none``\ ）選擇策略；所有
策略都經由 ``create_repo_retriever`` factory 建立：

* ``lexical``\ ──對 work-tree 的程式碼檔案做 BM25，加上 issue-aware
  的 query expansion。不需模型。
* ``semantic``\ ──以注入的 sentence-transformers embedder，依 query 的
  embedding 相似度排序檔案。
* ``structural``\ ──兩輪 lexical：第一輪命中檔案所定義的 symbol 與
  import 的模組會回饋進 query，讓 repo 自身的結構銳化第二輪。不需
  模型。
* ``graph``\ ──用 import graph 的鄰居擴展 lexical recall（top 命中
  import 的檔案，以及 import 它們的檔案）。不需模型、確定性。
* ``rerank``\ ──先取 lexical 候選，再由 review backend 讀其片段並
  回傳排序後的相關子集。
* ``block_rerank``\ ──在檔案層級 rerank 之上，backend 從逐檔候選中
  挑出相關的 ``def`` / ``class`` 區塊，維持行與 symbol 的高精確度。
* ``iterative``\ ──agentic 多輪檢索：每輪 backend 從候選池挑出相關
  區塊\ *並*\ 提出下一輪搜尋詞；選取結果持續累積，直到它表示已足夠
  或輪數預算用完。
* ``query_rewrite``\ ──一次便宜的 backend 呼叫把冗長的 issue 濃縮成
  聚焦的搜尋詞，附加到 query 後再交給 lexical base。
* ``hypothesis``\ ──model-in-the-loop 的 propose-verify 定位：每輪由
  模型提出可疑的（path、symbol、行號）假設，經靜態驗證（路徑／symbol
  是否存在、AST 行區間、import-graph caller）；被駁回的假設回饋為
  修正，確認的位置排最前。輪數由 ``--repo-context-rounds`` 限制。
* ``execution``\ ──execution-grounded 重排序：從變更／issue 文字挖出
  的 stack-trace frame，與 spectrum-based fault localization
  （Ochiai／Tarantula，對逐測試 coverage 計算；failing test 以程式
  方式提供時經 subprocess 收集）及 lexical 基礎排名做
  reciprocal-rank fusion；沒有任何訊號時退化為基礎 retriever。

work-tree 每個 retriever 實例只讀取並建索引一次（依 work-tree
memoize），不是每次查詢都重建──多輪策略是對已建好的索引重複查詢，
而非重讀整個 repository。
