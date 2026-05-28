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

``workflow_run`` 模式下要从 run payload 取得 PR 编号──请见 ``reviewmind.yml``
的内附注释。

合并前 Check Run gate
---------------------

``--gate-on`` flag 控制 PR head commit 上一个名为 ``reviewmind`` 的专属
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

1. 跑至少一次 ``REVIEWMIND_GATE_ON=error`` 的 PR，让 ``reviewmind`` 这个 Check
   Run 出现在 Checks 标签页。
2. **Settings → Branches → branch protection rule**\ ，选你的默认 branch。
3. 启用 **Require status checks to pass before merging**\ ，把 ``reviewmind``
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

CI 信号 + gate 一起用
---------------------

两个功能组合得很好：CI 信号让 findings 更可能包含真正的 bug（模型可以
grounding 在实际的失败），gate 再把这些更高质量的 finding 变成硬性合并
阻挡。

更严的设置可以再开 ``--rules-dir``\ （团队规则），让模型知道你的团队把
什么当 error、什么当 warning。
