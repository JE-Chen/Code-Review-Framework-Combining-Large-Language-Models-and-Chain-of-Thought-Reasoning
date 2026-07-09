Pre-commit hook、自我纠正、自动修补 PR
======================================

三项新增功能，把 prthinker 接到开发者日常流程的最后一哩。

Pre-commit hook（\ ``prthinker hook``\ ）
------------------------------------------

新增的 subcommand 会读 ``git diff --cached``\ 、跑 per-file pipeline，
若在设定之严重度下限有 finding 幸存即以非零码退出。配合
`pre-commit <https://pre-commit.com>`_ framework，prthinker 就成为
CI、IDE（MCP）、手动 CLI 之外的第四个触发点：

.. code-block:: yaml

   # 消费端 repo 之 .pre-commit-config.yaml
   repos:
     - repo: https://github.com/<your-org>/prthinker
       rev: v0.1.0
       hooks:
         - id: prthinker
           env:
             PRTHINKER_BACKEND: openai
             PRTHINKER_OPENAI_MODEL: gpt-4o-mini

``.pre-commit-hooks.yaml`` 提供两种 hook：

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - hook id
     - 退出码语义
   * - ``prthinker``
     - 任一 error 严重度 finding 即 exit 1（commit 被挡）。可用
       ``--block-on warning`` 或 ``--block-on none`` 覆盖。
   * - ``prthinker-advisory``
     - 永远 exit 0；finding 只打印到 stderr。适合在开 branch protection
       前作为过渡。

Cache 与 telemetry 在此一样可叠上；同一份 diff 重跑几乎一定命中缓存。

何时不要用
~~~~~~~~~~

* 若团队提交频率高、每次只 commit 很小的 WIP，hook 延迟会累积。改用
  ``prthinker-advisory``\ 、或把 hook 移到 ``pre-push`` 阶段。
* 若队友没有 API 额度，仅在 CI 也审查之 branch 上启用，避免「我能跑、
  你不能跑」的分裂。

自我纠正（\ ``--self-correct``\ ）
----------------------------------

``inline_findings`` step 产出 JSON 数组、dismissed filter 抑制过已知重复
之后，再向模型问一次：「以资深 reviewer 视角再读一次，哪些属于
noise / 重复 / 过度挑剔？」runner 把模型标记之 index 从清单删除后才
post inline review。

Prompt（\ :data:`codes.run.CoT_Prompts.finding_self_review.FINDING_SELF_REVIEW_TEMPLATE`\ ）
定义五类 noise（重复、过度挑剔、推测、同义反复、超范围）与四类保留
（明显之 correctness / security、附具体修正之可维护性、隐性 bug、团队
既有规则违规）。模型返回：

.. code-block:: text

   {
     "drop": [<1-based index>, ...],
     "reasons": ["...", ...]
   }

失败安全姿态
~~~~~~~~~~~~

:mod:`prthinker.self_review` 之 parser 故意宽容：模型输出格式错误时
返回\ **空 drop set**\ （不丢任何 finding），而非「全部丢」。此一不对称
是刻意的——错误地 post 一条 finding 可救（人可忽略），错误地删掉一条
真 bug 救不回。

成本
~~~~

每个文件多一次 backend call、与 finding 数量无关。开了 ``--cache`` 之后，
同一份 PR 反复触发只需付第一次的成本。

自动修补 draft PR（\ ``--auto-fix-threshold``\ ）
-------------------------------------------------

当幸存之 ``warning`` 严重度 + 带 ``suggestion`` block 之 finding 数 ≥
threshold，runner 会：

1. 开新 branch ``auto-fix/prthinker-pr-<N>``\ 。
2. 对每个受影响文件，由下而上应用 suggestion（保持后段行号稳定）。
   两条相交之 edit 以先到先赢处理；被挡掉之 edit 写入 skipped 报告。
3. 用单一固定消息 commit。
4. 推上 branch（\ ``--force-with-lease`` 让重跑安全）。
5. 开一个 **draft** PR 指向原 PR 之 base branch，body 摘要应用 / 跳过
   数量并列出变更文件。

原 PR 上仍保留其原有 inline review；auto-fix PR 是一个独立可合并之
artifact。作者检查 diff 后决定要不要合回原 branch 或 close。

严重度过滤
~~~~~~~~~~

只有 ``warning`` 之 suggestion 会被自动应用。\ ``error`` finding 仍保留
为 inline comment──原则是 error 需要人类判断「这个 patch 是否真的对」，
即便 patch 本身看起来没问题。\ ``info`` 之 ``suggestion`` 早于 sanitizer
阶段被剥掉。

冲突检测
~~~~~~~~

纯函数 :func:`prthinker.auto_fix.apply_suggestions_to_text` 返回
:class:`prthinker.auto_fix.ConflictReport`\ ，内含 ``applied``\ （成功
写入之 edit）与 ``skipped``\ （与既有 edit 相交而被挡之 edit + 挡住它
的 edit）两份清单。检测规则：edit 依 ``(start, end, finding_index)``
排序，按序走一遍；先到先赢。此函数不需 git 环境即可单元测试，见
``tests/test_auto_fix.py``\ 。

何时不要用
~~~~~~~~~~

* 若 CI 提供之 ``GITHUB_TOKEN`` 没有 push branch 之权限（fork PR
  常如此），push 步骤会失败。Auto-fix 最可靠的场景是同 repo PR。
* 若团队要求 signed commits，auto-fix 之默认 commit 不会被签。请在
  CI 端配置签署，或于要求签署之 branch 关闭此功能。

Issue 自动化（``--auto-file-issues``\ 、\ ``issue-autofix``）
-------------------------------------------------------------

两项功能补上审查回路外围的缺口\ ，GitHub 与 GitLab 皆支持
（平台差异全部收在 ``prthinker.issue_tracker`` 的 Strategy 层）：

**自动开 issue。** 落在 diff hunks 之外的 findings 无法以 inline
comment 张贴 —— 平台会拒绝 —— 过去只能留在 summary 文字里\ 。
``review-pr --auto-file-issues off-diff`` 把它们一一开成 tracker 上的
issue（``all`` 则每个 finding 都开）\ 。issue 正文嵌有指纹 marker
（path + category + 规范化 comment 的哈希\ ，刻意不含行号）\ ，让重跑
审查具幂等性：同一个问题在其 issue 尚未关闭时绝不重复开单\ 。单次最多
开 10 张新 issue\ ，且每次 API 调用皆为 best-effort —— tracker 挂掉
绝不弄坏审查本体\ 。

**Issue 自动修复。** ``issue-autofix`` 把 ``issue-fix`` 引擎跑完整条
回路：抓 issue\ 、定位相关文件\ 、提出必须逐字应用且语法有效的
find/replace 编辑\ ，可选择以测试命令把关\ ，然后开分支 / commit /
push\ ，开一个 draft fix PR（GitHub）或 MR（GitLab）\ ，其
``Fixes #N`` 于合并时自动关闭 issue\ ，并把链接评论回 issue\ 。
不加 ``--open-pr`` 则是纯 dry run\ 。两项功能可组成一个回路 ——
审查开 issue\ ，\ ``issue-autofix --issue-label`` 提出修复 ——
但每个 PR 都是 draft\ ，仍由人类决定是否合并\ 。

与其他功能之组合
----------------

三项新增可与既有 pipeline 自然叠合，不需要特殊处理：

* **hook ↔ cache**\ ：hook 重跑命中 CI 跑过之同一份 cache；相同 diff
  token 成本为零。
* **self-correct ↔ telemetry**\ ：多出之 backend call 与其他 ``generate``
  一样记录，于 ``prthinker stats`` 之 ``(backend, model)`` 字段中可见。
* **auto-fix ↔ gate**\ ：gate 结算发生在 auto-fix 之前，所以原 PR 之
  Check Run 反映「未修补」状态。作者合回 auto-fix PR 后，下一次推送会
  重新触发 gate 对修正后 diff。
* **auto-fix ↔ judge**\ ：judge verdict 套在原 PR；auto-fix PR 不自己再
  跑 prthinker（会循环）。

CLI flag 速查
-------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - 环境变量
     - 默认
   * - ``hook`` subcommand
     - 不适用
     - —
   * - ``--advisory``\ （仅 hook）
     - ``PRTHINKER_HOOK_ADVISORY``
     - ``false``
   * - ``--block-on {none,warning,error}``\ （仅 hook）
     - ``PRTHINKER_HOOK_BLOCK_ON``
     - ``error``
   * - ``--self-correct``
     - ``PRTHINKER_SELF_CORRECT``
     - ``false``
   * - ``--auto-fix-threshold N``\ （review-pr）
     - ``PRTHINKER_AUTO_FIX_THRESHOLD``
     - ``0``\ （关闭）
   * - ``--auto-fix-base-branch BRANCH``\ （review-pr）
     - ``PRTHINKER_AUTO_FIX_BASE_BRANCH``
     - *(从原 PR 抓)*
