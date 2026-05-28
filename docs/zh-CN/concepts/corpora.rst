学习语料：dismissed 与 accepted
====================================

Reviewer 维护两份 JSONL store，捕捉 PR 作者长期对 finding 的反应。两者都由
``harvest-*`` CLI 指令产生，并在服务器启动时被读入。

不对称的角色
------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Store
     - 用途
     - 信号来源
   * - ``dismissed.jsonl``
     - *过滤* 候选 finding（太相似就丢掉）
     - 👎 reaction、「false positive」回复、被忽略的评论
   * - ``accepted.jsonl``
     - *补强* prompt（top-K 示例注入）
     - 含 ``Apply suggestion`` commit 的 PR

这个不对称是刻意的。Dismissal 是负向训练信号（\ *下次别再产出像这样的东西*\ ），
所以做成基于相似度的输出过滤。Accepted suggestion 是正向训练信号
（\ *这种建议在这个 repo 有效*\ ），所以以 in-context exemplar 形式在 prompt
构建时注入。

Store schema
------------

``dismissed.jsonl``\ ──每行一个 JSON object：

.. code-block:: json

   {
     "path": "src/auth.py",
     "comment": "别把 token 用明文存",
     "reason": "thumbs-down reaction",
     "diff_snippet": "@@ -3,1 +3,3 @@\n+token = req.json()['token']"
   }

``accepted.jsonl``\ ──每行一个 JSON object：

.. code-block:: json

   {
     "path": "src/auth.py",
     "comment": "用 Path.resolve 把路径正规化",
     "suggestion": "    path = Path(path).resolve()",
     "pr_number": 137
   }

两者都是 append-only──harvest 指令绝不覆盖既有行，所以 ``--max-prs 100``
跑完再用 ``--max-prs 200`` 跑一次是安全的。读不过 JSON 的行会被 warning
略过。

Harvest
-------

.. code-block:: bash

   # 抓 👎 与 dismissal-keyword reply
   reviewmind harvest-dismissed \
       --repo owner/name \
       --max-prs 100 \
       --out .reviewmind/dismissed.jsonl

   # 扫含「Apply suggestion」commit 的 PR，
   # 把那些 PR 上有 ```suggestion``` 区块的评论全部保留
   reviewmind harvest-accepted \
       --repo owner/name \
       --max-prs 100 \
       --out .reviewmind/accepted.jsonl

Dismissal 关键字 list 目前是写死的（混合英文与简体中文）：\ *false positive、
wontfix、not relevant、ignore this、intentional、by design*\ ，外加「误判」、
「不是问题」、「不修」、「已讨论」、「故意」、「预期」、「本来就是」等。

Accepted 收集是 best-effort：GitHub 不会把「Apply suggestion」commit 反查
连到产出它的 review comment，所以 harvester 假设在含此 commit 的 PR 上，
任何附 ``suggestion`` 区块的评论都被采纳了。误收的部分在 K=3 时会被稀释。

相似度过滤（dismissed）
-----------------------

服务器端 ``DismissedFilter`` 在 boot 时对每条 stored ``comment`` 各 embed
一次，使用与 RAG 同一支 ``codes/util/faiss_util.get_embedding``\ 。对每个
候选 finding，filter 会 embed finding 的 ``comment`` 文本，跟所有 stored
示例算 cosine。Finding 被丢掉的条件：

.. math::

   \max_{e \in \text{store}} \langle \mathrm{emb}(f.\text{comment}),
   \mathrm{emb}(e.\text{comment}) \rangle \geq \tau

默认 ``τ = 0.85``\ 。可通过 ``REVIEWMIND_DISMISSED_THRESHOLD`` 覆盖。

Top-K 示例（accepted）
----------------------

``AcceptedExamplesRetriever`` 逻辑一样，但返回超过自己（较低）阈值的前 K
个结果，而不是过滤。被选中的示例会渲染进 ``inline_findings`` prompt 的
``## Examples of past advice that was accepted in this repo`` 区块，位置
在 diff 本身之前。

默认：\ ``K = 3``\ 、\ ``τ = 0.6``\ 。可通过 ``REVIEWMIND_ACCEPTED_TOP_K``\ 、
``REVIEWMIND_ACCEPTED_THRESHOLD`` 覆盖。

冷启动
------

两个过滤器在 store 为空或缺文件时都是 no-op──启动 log 会显示
``filter disabled`` / ``exemplars disabled``\ 。没有 store 也能正常跑 reviewer
多久都行；语料是质量加成，不是必要依赖。

研究用途
--------

这两个文件是从 production review 流量中积累出来的标注负例 + 正例语料。
可以用来衡量：

* 各类 finding 随时间变化的 dismissal rate
* 相似度过滤的丢弃率（对 held-out 人工标注集计算 precision / recall）
* Exemplar 注入是否能改变产出 suggestion 的分布

原始稿件中的对应数字请见 ``paper/``\ 。
