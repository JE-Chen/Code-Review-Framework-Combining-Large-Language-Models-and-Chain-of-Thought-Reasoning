CoT pipeline
============

Pipeline 对一份 code diff 跑一连串固定的 *review steps*\ 。每个 step 产生一段
markdown；后续 step 可以从共享的 ``ReviewContext`` 读前面的输出。默认
registry 有五个 step；逐文件模式会多开一个输出结构化 finding 的 step。

Step 顺序
---------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Step
     - 它产出什么
   * - ``first_summary``
     - 第一轮 PR summary──改了什么、为什么、有哪些风险。
   * - ``first_code_review``
     - 对 diff 做的 free-form review，依据 global rules。
   * - ``linter``
     - 只看 style / formatting 问题。
   * - ``code_smell``
     - 可维护性与设计层面的问题。
   * - ``total_summary``
     - 整合：读前面四个输出加 diff，给出最终判断与合并建议。
   * - ``inline_findings``
     - *(仅 per-file)* 输出 ``{line, severity, comment, suggestion?}``
       的 JSON 数组，由 runner 转为 GitHub inline review comment。

前五个住在 ``codes/run/CoT_Prompts/``\ ，由 ``build_global_rule_template``
包起来，让 RAG 规则与 per-repo 规则以一致的方式注入。\ ``inline_findings``
跳过这个 wrap，这样模型比较可能输出纯 JSON。

两种执行模式
------------

Single-pass
   对整份 diff 跑一个 prompt sweep。便宜，但模型只看得到 file headers，
   不容易说「是哪一行」有问题。没有 inline review。

Per-file
   Diff 被切成一个个 ``FileDiff``\ ，pipeline 对每个文件跑一次，每跑可以追加
   ``InlineFindingsStep`` 来产 per-line 的 ``InlineFinding``\ 。Runner 聚合
   结果，套用 dismissed filter，发 GitHub review。

Per-file 是 production 设定；内附的 GHA workflow 默认开启。

Diff 解析
---------

``reviewmind.diff.parse_unified_diff`` 把 unified diff 切成 ``FileDiff``
对象，并跟踪每个文件在 *新侧* 出现过的 line numbers。这份集合驱动 line
校验：任何 ``InlineFinding`` 指向不在 diff 内的行都会在送到 GitHub 前就
被丢掉。GitHub 本来就会拒绝针对被删除行的评论，先在 client 侧丢干净可以
让 review API 调用更干净。

Findings extraction
-------------------

``inline_findings`` step 要求模型输出 JSON 数组。
``reviewmind.findings`` 的解析器刻意做得宽容：

1. 剥掉 Markdown fenced-code 包装（\ ``\`\`\`json … \`\`\```\ ）。
2. 找最外层的 ``[ ... ]`` 区块。
3. 用 ``json.loads`` 解；失败就退回 per-object regex。
4. 每条对 ``InlineFinding`` Pydantic schema 做校验──丢掉格式错的。
5. ``line`` 不在该文件 diff lines 内的也丢掉。
6. *sanitize* ``suggestion`` 字段：丢掉建议但保留 textual comment，当以下
   任一条件成立：

   * severity 为 ``info``\ （prompt 禁止对 info 级别给 suggestion）。
   * ``start_line > line``\ 。
   * 多行 suggestion 的行数对不上 range。
   * ``start_line`` 不在 diff 内。

错的 suggestion 比没有 suggestion 更糟（reviewer 可能盲目应用），所以保留
门槛设得高。

Dismissed filter
----------------

解析后，可选的 ``DismissedFilter`` 会把 comment 文本与既有 dismissed 示例
太相似的 finding 丢掉。store 的 schema 请见 :doc:`corpora`。

输出通道
--------

每个 PR 上 reviewer 会写三个通道：

* **总结评论**\ ──一条 PR conversation 评论，靠 sentinel marker upsert，
  让重跑时不会刷屏。Per-file 模式下每个文件会渲染成可折叠的
  ``<details>`` 区块。
* **Inline review**\ ──一条 ``POST /pulls/:n/reviews``\ ，每个幸存 finding
  各自一条评论。Suggestion 区块在 GitHub UI 上会渲染成一键 *Apply
  suggestion* 按钮。
* **Check Run**\ ──开始时开为 ``in_progress``\ ，根据 ``--gate-on`` 与 surviving
  findings 结算为 ``success`` 或 ``failure``\ 。
