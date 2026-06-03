CI 信号与合并前 gate
====================

两个功能让 reviewer 从「丢一句评论」变成「依数据行动」：\ **CI 失败信号**
（输入端）与 **Check Run gate**\ （输出端）。

CI 失败信号
-----------

开 ``--include-ci-signals`` 时，runner 会抓 PR head SHA 已经完成的
Actions runs，挑出失败的，把每个失败 job 的 log 末端取出，包成 fenced
区块**前置到 diff** 再跑 pipeline：

.. code-block:: text

   <!-- CI Failure Signals -->
   # CI Failure Signals

   These are failed jobs from the latest CI run on this PR head.
   Correlate findings with the failures below when applicable; do NOT
   invent failures not present here.

   ## CI / test-python (failure)

   ```
   E   AssertionError: expected 1, got 2
   E       at tests/test_auth.py:42
   ...
   ```

   <!-- End CI Failure Signals -->

   diff --git a/auth.py b/auth.py
   ...

模型现在有 runtime context。Finding 可以把 flagged 行与具体测试失败对上
（「\ ``auth.py:42`` 这个改动对应到上面的 ``test_auth`` 回退」）。

可调参数
~~~~~~~~

* ``--ci-signal-max-jobs N``\ ──最多纳入几个失败 job。默认 ``5``\ ，每个 job
  独立处理。
* ``--ci-signal-tail-chars N``\ ──每个 job 保留多少字符（从末端切）。默认
  ``4000``\ 。模型通常只会用到最后几百字符。

两个旋钮都在 prompt token 预算与信号覆盖率之间做权衡。

权限
~~~~

Actions API 需要 ``actions: read`` 权限。内附 workflow 已声明；fork 时请
保留。

时机
~~~~

默认的 ``pull_request`` trigger 一推就跑，比任何 CI 都早。Runner 拿到的是
「跑这一刻 head SHA 上已存在的 CI 信号」──通常是首次推送什么都拿不到，
之后每次推送拿到的是上一次 run 的 log。

如果你要 reviewer 等 CI 跑完：

.. code-block:: yaml

   on:
     workflow_run:
       workflows: ["CI"]
       types: [completed]

``workflow_run`` 模式下要从 run payload 取得 PR 编号──请见 ``prthinker.yml``
的内附注释。

合并前 Check Run gate
---------------------

``--gate-on`` flag 控制 PR head commit 上一个名为 ``prthinker`` 的专属
Check Run。CLI 会：

1. 审查开始时 ``POST /check-runs``\ ，状态 ``status: in_progress``\ 。
2. Pipeline 跑完（含 dismissed filter）后，依严重度分类计算 surviving
   findings 数量。
3. ``PATCH /check-runs/:id`` 把 ``status`` 设为 ``completed``\ ，\ ``conclusion``
   根据设置的 gate floor 决定。

结算逻辑
~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - ``--gate-on``
     - 何时结算为 ``failure``
     - 否则
   * - ``none``
     - 永远不
     - 永远 ``success``
   * - ``error``
     - ``error`` 数 ≥ 1
     - ``success``
   * - ``warning``
     - ``error`` 或 ``warning`` 数 ≥ 1
     - ``success``\ （只有 ``info`` 时）

``info`` 严重度的 finding **永远不会**\ 触发 gate。它们是团队可能在意也可能
不在意的小问题──如果连这也挡合并，merge friction 会爆炸。

设为 branch protection
----------------------

把 reviewer 真的接到挡合并：

1. 跑至少一次 ``PRTHINKER_GATE_ON=error`` 的 PR，让 ``prthinker`` 这个 Check
   Run 出现在 Checks 标签页。
2. **Settings → Branches → branch protection rule**\ ，选你的默认 branch。
3. 启用 **Require status checks to pass before merging**\ ，把 ``prthinker``
   加进必需检查。

之后，只要 PR 还有 error 严重度的 finding 就无法合并。作者会直接看到 gate
结果（Check Run summary 会列出 error / warning / info 的数量分布）。

异常情况
~~~~~~~~

* **Pipeline crash**\ ──CLI 的 exception handler 会 PATCH Check Run 为
  ``conclusion: failure``\ ，\ ``title: "Reviewer crashed"``\ 。PR 不会永远卡在
  「跑中」的状态。
* **空 diff**\ ──reviewer 直接跳过：不开 Check Run、不贴评论。
* **Findings 被过滤到零**\ ──gate 结算为 ``success``\ 。总结评论仍会贴上来
  让作者知道 reviewer 有跑过。

贴出审查：评论与 inline 建议
----------------------------

加上 ``--pr-overview``\ （环境变量 ``PRTHINKER_PR_OVERVIEW``）时，总结最上方
会多一段不需模型的 **What this PR does (preliminary)** 区块，完全由 PR 的
commit messages 与变更文件\ *确定式*\ 生成：文件／目录／扩展名分布、
conventional-commit 类型统计（``feat (3) · fix (1)``），以及 commit 主旨列表。
它是\ *上下文*\ 而非结论──回答「改了什么」，下方的摘要才回答「好不好」──
同样固定在会被原地更新的 part-1 评论，每次审查都会刷新。

每份逐文件总结最上方都有一个 **Review at a glance** 摘要──白话的状态
（🔴 changes requested／🟡 review suggested／🔵 minor notes／✅ looks good）、
按严重度分类的 finding 数量、已审查／有 finding／干净的文件分布，以及
finding 最多的\ *热点*\ 文件。它固定在会被原地更新的 part-1 评论最上方，所以
每次重新审查都会原地改写，永远反映最新一次的结果。

逐文件区块会\ **按严重度排序**\ （有 error 的文件在前，再来 warning、info，
同级再比 finding 数），每个文件的徽章改用严重度图标（``🔴2 🟡1``）而非单纯
数字。在 GitHub 上，每个文件名──热点行与区块标头──都是\ **深层链接**\ ，
直接跳到该文件在 Files-changed 分页的第一个 finding（GitHub Enterprise 主机
请设置 ``PRTHINKER_PR_FILES_URL``）。

完整的逐文件审查可能达数百 KB，远超过 GitHub 单条评论 65 536 字符的上限。
与其截断，总结会\ **切分成多条评论**\ ：只在整个文件区块之间切（绝不切在
区块中间），第一条之后的每一条都带有 ``Part k/N`` 标记。跨多次 push 时，
这些分页会以 marker 对齐\ ──既有评论原地更新、不足的分页新增、上一轮较长
评论残留的多余分页删除，残缺的旧分页不会留下。GitHub 以外的平台则退回
单条评论（溢出的内容留在 job log 里）。

加上 ``--findings-only``\ （环境变量 ``PRTHINKER_FINDINGS_ONLY``）时，总结
\ **只**\ 列出有 finding 的文件；干净的文件会折叠成一行
``N file(s) reviewed with no findings — hidden``\ ，而整个 PR 零 finding 时
则折叠成一行 ``✅ No findings`` 确认信息，而非完整的空结果。在大型但大多
干净的 PR 上，这通常能把多条分页的总结缩回单条评论。

``--hide-info``\ （环境变量 ``PRTHINKER_HIDE_INFO``）会把 ``info`` 严重度的
finding 从总结中略去──数量徽章、at-a-glance 统计、热点排名都不计入它们，
而只有 info finding 的文件会被视为干净。这只影响显示：diff 上的 inline
review 与合并 gate 仍会看到所有 finding。

加上 ``--pr-labels``\ （环境变量 ``PRTHINKER_PR_LABELS``）时，reviewer 还会
在 PR 上贴两个受管理的标签──规模（``prthinker/size-xs`` … ``size-xl``\ ，
按审查文件数）与状态（``prthinker/changes-requested`` / ``review-suggested``
/ ``clean``）──让 PR 列表不必逐一点开就能扫描。只有 ``prthinker/`` 前缀的
标签会跨 run 对齐，人工贴的标签完全不动。

inline 建议\ ──diff 上一键 *Apply suggestion* 的区块\ ──会以另一个 PR
review 贴出。新的 review 会\ **先**\ 送出，之后才移除上一轮的 inline 评论，
而且移除时会排除刚刚送出的 review。先贴再移除代表：当送出被拒（只要有任何
一条评论指到 diff hunk 范围外的行，GitHub 会 422 拒绝\ *整个*\ review）时，
上一轮的建议仍会保留，而不是在失败的重贴之前就被清掉。

加上 ``--check-annotations``\ （环境变量 ``PRTHINKER_CHECK_ANNOTATIONS``）时，
gate 的 Check Run 还会带逐行标注（每个 finding 一条，按严重度为
``failure`` / ``warning`` / ``notice``）。它们显示在 Files-changed 与 Checks
分页，是 inline review 之外的\ *并行*\ 通道：单一坏行只会被单独丢弃，而不会
422 拖垮整批；且 GitHub 会跨请求累加，因此超过 50 个 finding 的审查会分成
数次更新送出。

CI 信号 + gate 一起用
---------------------

两个功能组合得很好：CI 信号让 findings 更可能包含真正的 bug（模型可以
grounding 在实际的失败），gate 再把这些更高质量的 finding 变成硬性合并
阻挡。

更严的设置可以再开 ``--rules-dir``\ （团队规则），让模型知道你的团队把
什么当 error、什么当 warning。
