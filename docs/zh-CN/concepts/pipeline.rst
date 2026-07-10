CoT pipeline
============

Pipeline 对一份 code diff 跑一连串 *review steps*\ 。每个 step 产生一段
markdown；后续 step 可以从共享的 ``ReviewContext`` 读前面的输出。默认
registry 有五个 step──这条五步链是完整（deep 层）的行为；加上
``--step-plan adaptive`` 时会逐文件裁剪（见下文）。逐文件模式会多开
一个输出结构化 finding 的 step。

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

前五个由 ``build_global_rule_template`` 包起来，让 RAG 规则与 per-repo
规则以一致的方式注入。\ ``inline_findings`` 跳过这个 wrap，这样模型比较
可能输出纯 JSON。所有 prompt 模板随包内置于 ``prthinker/prompts/``\ ，
逐字节镜像自规范的 ``codes/run/CoT_Prompts/`` 语料。

另有三个只在降级审查深度时使用的 prompt-backed step（见下一节）：

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Step
     - 它产出什么
   * - ``compact_review``
     - 整条分析链的单调用替代品──一个 prompt 覆盖正确性、lint 级别
       问题、code smell 与简短结论，取代五次模型调用。
   * - ``unified_review``
     - **一次**\ 模型调用同时产出 findings JSON、简短分析摘要与判定；
       pipeline 会把 payload 拆回历史沿用的 ``inline_findings`` /
       ``compact_review`` result key。
   * - ``batch_findings``
     - trivial 文件的多文件合批 prompt：多个小 diff 并成一次调用审查，
       返回的扁平 findings 数组依 ``path`` 标签拆回逐文件 finding。

自适应 step 规划（``--step-plan adaptive``）
--------------------------------------------

默认（``--step-plan full``）每个文件都跑所有已配置的 step。加上
``--step-plan adaptive`` 时，一个纯函数、确定性的规划器
（``prthinker.step_planner``）会为每个 ``FileDiff`` 指派四个深度层级
之一，只看 diff 本身（大小、文件种类）加上 pipeline 本来就会算的
逐文件风险分。风险优先于大小：对历史上脆弱的文件做三行改动绝不算
trivial。

skip
   机器生成的文件──lockfile（``package-lock.json``\ 、
   ``poetry.lock`` 等）、minified bundle、生成的 artifact、
   ``vendor/`` / ``node_modules/`` 这类 vendored 目录──以及纯空白
   的重排版。零模型调用、零检索，但文件仍会出现在总结中并标为
   skipped，让「按策略跳过」看得见而非无声消失。

trivial
   文档／声明式配置后缀（``.md``\ 、\ ``.rst``\ 、\ ``.json``\ 、
   ``.yaml``\ 、\ ``.toml`` 等）或至多 5 行变更。只留下产出输出的
   step（inline findings、walkthrough）。整份计划只剩 findings pass
   的 trivial 文件会\ **合批**\ ：每次模型调用最多 6 个文件／24 000
   字符的 diff，走 ``batch_findings`` prompt。返回数组依 ``path``
   标签拆回逐文件，经过与单文件审查完全相同的校验解析器，且每个文件
   的 findings 各自独立缓存，differential review 仍逐文件生效。

standard
   介于两者之间的一切。一次 ``unified_review`` 调用返回 findings
   JSON 加简短摘要与判定，拆回历史沿用的 ``inline_findings`` /
   ``compact_review`` result key，因此 findings 解析、报告、gate
   全部不变。加上 ``--counterfactual``\ （它消费解析后的 findings）
   时，standard 层改为保留两次调用的 ``compact_review`` +
   ``inline_findings`` 形态。

deep
   变更 200 行以上，或风险分 ≥ 0.7──风险覆写不论大小或文件种类都
   生效。保留完整五步链加上所有已配置的额外 step。

降级层级同时也会压低生成上限：trivial 为 4096 个新 token、standard
为 8192；deep 维持 pipeline 全局预算。所选层级会记录在每个文件的
``step_outputs`` 之 ``step_plan`` key，随审查结果进入序列化输出与
报告，深度决策全程可审计。

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

``prthinker.diff.parse_unified_diff`` 把 unified diff 切成 ``FileDiff``
对象，并跟踪每个文件在 *新侧* 出现过的 line numbers。这份集合驱动 line
校验：任何 ``InlineFinding`` 指向不在 diff 内的行都会在送到 GitHub 前就
被丢掉。GitHub 本来就会拒绝针对被删除行的评论，先在 client 侧丢干净可以
让 review API 调用更干净。

Findings extraction
-------------------

``inline_findings`` step 要求模型输出 JSON 数组。
``prthinker.findings`` 的解析器刻意做得宽容：

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
