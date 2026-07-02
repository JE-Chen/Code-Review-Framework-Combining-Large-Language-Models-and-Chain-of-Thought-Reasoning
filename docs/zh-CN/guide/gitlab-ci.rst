GitLab CI 集成
==============

审查器是\ **与 forge 无关（forge-agnostic）**\ 的:同一个 runner CLI
(``python -m prthinker review-pr``) 通过单一
:class:`~prthinker.platforms.base.PlatformAdapter` 策略,即可驱动 GitHub、
GitLab 或 Gitea 的 merge request,用 ``--platform``\ （或
``$PRTHINKER_PLATFORM``\ ）选择。项目已内置可直接使用的 GitLab pipeline,
位于 repo 根目录的 ``.gitlab-ci.yml``\ 。

如何对应到 GitLab
-----------------

审查路径里没有任何 GitHub 专属的东西。CLI 会自动解析 GitLab-CI 的环境变量,
因此 pipeline 无需传任何标识参数:

.. list-table::
   :header-rows: 1
   :widths: 38 27 35

   * - GitLab-CI 变量
     - CLI 参数
     - 含义
   * - ``$CI_PROJECT_PATH``
     - ``--repo``
     - ``group/project`` 路径
   * - ``$CI_MERGE_REQUEST_IID``
     - ``--pr-number``
     - merge request 的 iid
   * - ``$GITLAB_TOKEN``
     - ``--github-token``
     - API token（需 ``api`` scope）
   * - ``$PRTHINKER_PLATFORM=gitlab``
     - ``--platform``
     - 选用 GitLab adapter

adapter 会把总结贴成 merge-request note、把 findings 贴成 diff 上的
inline 讨论串,并把 gate 设成名为 ``prthinker`` 的 commit status──
这就是 GitHub Check Run 在 GitLab 的对应物。

单一 job,没有 matrix
---------------------

和 GitHub Actions workflow 不同,这里没有 ``enumerate``\ ／matrix／
``aggregate`` 的拆分。那套 fan-out 只是为了把单一共享 GPU backend
分流到逐文件 runner 上。``review-pr`` 会在同一个进程里审查所有变更文件,
并直接贴出总结、inline 讨论与 gate,所以 GitLab pipeline 就是一个
``review-pr`` job。

需要的 CI/CD 变量
-----------------

在 **Settings → CI/CD → Variables** 设置以下变量（token 请勾选
\ *Masked*\ ）:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - 变量
     - 用途
   * - ``GITLAB_TOKEN``
     - 具 ``api`` scope 的 Project／Group access token 或 PAT。内置的
       ``CI_JOB_TOKEN`` 无法贴 merge-request note。
   * - ``PRTHINKER_BACKEND_URL``
     - 推理 backend 的 HTTPS URL;CI runner 本身不需要 GPU。
   * - ``PRTHINKER_BACKEND_API_KEY``
     - backend 的 bearer token（可选）。

Pipeline 文件
-------------

内置的 ``.gitlab-ci.yml`` 精简成单一 job,核心形状如下:

.. code-block:: yaml

   prthinker-review:
     stage: review
     image: python:3.12-slim
     rules:
       - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
     variables:
       PRTHINKER_PLATFORM: "gitlab"
       PRTHINKER_BACKEND: "remote"
       PRTHINKER_REMOTE_URL: "$PRTHINKER_BACKEND_URL"
       PRTHINKER_REMOTE_API_KEY: "$PRTHINKER_BACKEND_API_KEY"
       PRTHINKER_GATE_ON: "error"
     script:
       - pip install -e ".[runner]"
       - python -m prthinker review-pr

``rules`` 子句对应 GitHub 的 ``pull_request`` 触发:此 job 只在
merge-request pipeline 上执行。

挡下合并
--------

gate 是 ``prthinker`` 这个 commit status,而不是 pipeline 本身的成功／
失败。要硬性挡下合并,请在 **Settings → Merge requests**\ （merge checks）
或受保护分支规则里「要求该状态通过」──这与 GitHub 要求 Check Run
的模式相同。总结 note 会列出 error／warning／info 的数量,作者一眼就能
看出是什么触发了 gate。

功能对等
--------

审查本身──CoT pipeline、RAG、学习语料、inline suggestion 与 gate──
在各 forge 之间完全相同，而且 GitLab adapter 也覆盖了平台附加功能：

* **CI 失败信号**\ （\ ``--include-ci-signals``\ ）通过
  ``/projects/:id/jobs/:id/trace`` 读取失败 pipeline job 的 trace 尾段。
* **Auto-fix**\ （\ ``--auto-fix-threshold``\ ）改开一个应用建议的
  ``Draft:`` merge request──GitHub 草稿 PR 的 MR 对应物。
* **Labels、描述摘要与 PR 摘要**\ （\ ``--pr-labels``\ 、
  ``--pr-body-summary``\ 、``pr-summary`` 子命令）会 reconcile 受管
  MR labels、upsert 描述中的标记区块，并维护独立的摘要 note。过长的
  评审会分页成多个 note；上一轮较长运行留下的残页会被删除。
* **判定**\ 映射到 approvals API：``APPROVE`` 核准 MR，
  ``REQUEST_CHANGES`` 撤销先前的核准（best-effort──token 无法核准时
  记一行警告，判定仍保留在 discussion 正文前缀）。
* Inline findings 发布前会先比对 MR 的 diff hunk 过滤，幻觉行号只会
  损失一条 finding，而不是连续多个失败的 discussion POST。

自托管（self-hosted）GitLab 只要用 ``--platform-base-url``\ （或
``$PRTHINKER_PLATFORM_BASE_URL``\ ）把 adapter 指向你的实例 API 即可,
例如 ``https://gitlab.example.com/api/v4``\ 。同样的方式配合
``--platform gitea`` 即可服务 Gitea。
