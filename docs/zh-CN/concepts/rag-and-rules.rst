RAG 与规则包
============

Reviewer 的 prompt 留了一个专门放 *规则* 的槽位，会合并两种来源：全局检索
出的 best-practice rules（RAG）与 repo 自带的常驻团队规则。

全局 RAG
--------

``codes/util/faiss_util.py`` 用 ``Qwen/Qwen3-Embedding-4B`` 对
``datas/RAG_data/rag_data.py`` 中的 ``rule_docs`` 建立 ``IndexFlatIP``
（L2-normalised 向量）。Index 只在 module import 时建一次──查询成本低。

Retriever 接口位于 ``prthinker.rag.RAGRetriever``\ 。提供三个实现：

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

``--rules-dir`` flag（环境变量 ``PRTHINKER_RULES_DIR``\ ）会递归读取目录下所有
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

   from prthinker.rag import RAGRetriever

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

Repository-context 检索策略
---------------------------

在规则槽之外，逐文件审查 prompt 还可以前置从本地 work-tree
（``--repo-context-workdir``）检索出的跨文件\ *repository context*\ 。
``--repo-context-strategy``\ （环境变量
``PRTHINKER_REPO_CONTEXT_STRATEGY``\ ，默认 ``none``\ ）选择策略；所有
策略都经由 ``create_repo_retriever`` factory 构建：

* ``lexical``\ ──对 work-tree 的代码文件做 BM25，加上 issue-aware
  的 query expansion。不需模型。
* ``semantic``\ ──以注入的 sentence-transformers embedder，按 query 的
  embedding 相似度排序文件。
* ``structural``\ ──两轮 lexical：第一轮命中文件所定义的 symbol 与
  import 的模块会回馈进 query，让 repo 自身的结构锐化第二轮。不需
  模型。
* ``graph``\ ──用 import graph 的邻居扩展 lexical recall（top 命中
  import 的文件，以及 import 它们的文件）。不需模型、确定性。
* ``rerank``\ ──先取 lexical 候选，再由 review backend 读其片段并
  返回排序后的相关子集。
* ``block_rerank``\ ──在文件级 rerank 之上，backend 从逐文件候选中
  挑出相关的 ``def`` / ``class`` 区块，保持行与 symbol 的高精确度。
* ``iterative``\ ──agentic 多轮检索：每轮 backend 从候选池挑出相关
  区块\ *并*\ 提出下一轮搜索词；选取结果持续累积，直到它表示已足够
  或轮数预算用完。
* ``query_rewrite``\ ──一次便宜的 backend 调用把冗长的 issue 浓缩成
  聚焦的搜索词，附加到 query 后再交给 lexical base。
* ``hypothesis``\ ──model-in-the-loop 的 propose-verify 定位：每轮由
  模型提出可疑的（path、symbol、行号）假设，经静态验证（路径／symbol
  是否存在、AST 行区间、import-graph caller）；被驳回的假设反馈为
  修正，确认的位置排最前。轮数由 ``--repo-context-rounds`` 限制。
* ``execution``\ ──execution-grounded 重排序：从变更／issue 文本挖出
  的 stack-trace frame，与 spectrum-based fault localization
  （Ochiai／Tarantula，对逐测试 coverage 计算；failing test 以程序
  方式提供时经 subprocess 收集）及 lexical 基础排名做
  reciprocal-rank fusion；没有任何信号时退化为基础 retriever。

work-tree 每个 retriever 实例只读取并建索引一次（按 work-tree
memoize），不是每次查询都重建──多轮策略是对已建好的索引重复查询，
而非重读整个 repository。
