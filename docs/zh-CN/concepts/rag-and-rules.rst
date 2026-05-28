RAG 与规则包
============

Reviewer 的 prompt 留了一个专门放 *规则* 的槽位，会合并两种来源：全局检索
出的 best-practice rules（RAG）与 repo 自带的常驻团队规则。

全局 RAG
--------

``codes/util/faiss_util.py`` 用 ``Qwen/Qwen3-Embedding-4B`` 对
``datas/RAG_data/rag_data.py`` 中的 ``rule_docs`` 建立 ``IndexFlatIP``
（L2-normalised 向量）。Index 只在 module import 时建一次──查询成本低。

Retriever 接口位于 ``reviewmind.rag.RAGRetriever``\ 。提供三个实现：

* ``FaissRAGRetriever``\ ──in-process 包住 FAISS index。需要加载 embedding
  模型（约 8 GB VRAM）。用在推理服务器端。
* ``RemoteRAGRetriever``\ ──POST 到服务器的 ``/rag`` endpoint。让薄 runner
  不必绑 embedding 模型。GitHub Action 用这个。
* ``NoOpRetriever``\ ──返回 ``[]``\ 。做 pure-LLM baseline ablation 时用得到。

Threshold
~~~~~~~~~

``--rag-threshold``\ （默认 ``0.7``\ ）会丢掉与 query cosine 低于此值的文档。
这个旋钮影响最大──太低 prompt 会塞一堆不相关规则；太高就饿死模型。

Per-repo 规则包
---------------

``--rules-dir`` flag（环境变量 ``REVIEWMIND_RULES_DIR``\ ）会递归读取目录下所有
``*.md``\ （依路径排序），把每个文件的内容当成一条规则，\ **接在 RAG 检索出
的规则后面**\ 注入 prompt。

与 RAG 规则有两个重要差异：

* **常驻**\ ──不做相似度过滤。团队已经把它 check 进 repo 表示「就是要适用」，
  所以一律带上。
* **一档一条**\ ──让 git diff 容易审计。

目录结构示例::

   ./team-rules/
   ├── 010-imports.md
   ├── 020-error-handling.md
   ├── 030-logging.md
   └── 040-database.md

每个文件应该是一则简短易读的规则：

.. code-block:: markdown

   # 数据库查询

   - 一律使用 parameterised query，不要用 f-string 拼 SQL。
   - 多语句事务要用 `with conn:` 包起来。
   - 操作 `users` 表的查询必须带 `WHERE user_id = ?` 条件，否则拒绝。

规则怎么进到 prompt
-------------------

规则槽的唯一真实来源是 ``codes/run/CoT_Prompts/global_rule.py``\ 。Pipeline
调用 ``build_global_rule_template(prompt=..., rag_rules=merged_list)``\ ，
而 ``merged_list`` 是 *RAG 检索出的规则* + *--rules-dir 规则* 的串接。

两种规则都会渲染进 prompt 的
*"8. RAG Rules (Retrieval-Augmented Guidance)"* 段。

接线图
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

继承 ``RAGRetriever``\ ：

.. code-block:: python

   from reviewmind.rag import RAGRetriever

   class HybridRetriever(RAGRetriever):
       """同时返回 BM25 + FAISS 结果并去重。"""

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

Pipeline 对 retriever 的唯一契约就是 ``retrieve(str) -> list[str]`` 这个
方法──没有 global side effect、不要求 setup 顺序。
