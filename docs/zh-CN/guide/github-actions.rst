GitHub Actions 集成
===================

Reviewer 内附一份可直接用的 workflow：\ ``.github/workflows/reviewmind.yml``\ 。
它在 ``pull_request`` ``opened`` / ``synchronize`` / ``reopened`` 时触发，
通过同一个 PR 回贴 review。

必需 secrets
------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Secret
     - 用途
   * - ``REVIEWMIND_BACKEND_URL``
     - 你自己部署的推理服务器基础 URL
       （例如 ``https://gpu-host.internal:8000``\ ）。
   * - ``REVIEWMIND_BACKEND_API_KEY``
     - 可选的 bearer token，会以 ``Authorization: Bearer ...`` 发送。

在 **Settings → Secrets and variables → Actions** 设置。

必需权限
--------

Workflow 声明：

.. code-block:: yaml

   permissions:
     contents: read         # checkout
     pull-requests: write   # upsert 总结评论、提交 inline review
     checks: write          # 打开与结算合并前的 Check Run gate
     actions: read          # 抓 CI 失败 job 的日志

若你 fork 这份 workflow，请保留同样的权限，否则功能会被默默跳过。

可调整的环境变量
----------------

Workflow 把最常用的 flag 都暴露成环境变量，这样不用改 Python 也能改行为：

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - 变量
     - 默认
     - 效果
   * - ``REVIEWMIND_BACKEND``
     - ``remote``
     - 设为 ``local`` 改在 runner 上加载 Qwen（需要 self-hosted GPU runner）。
   * - ``REVIEWMIND_USE_REMOTE_PIPELINE``
     - ``true``
     - 用 ``/review`` 单回合调用，而不是每个 step 都打一次 ``/ask``\ 。
   * - ``REVIEWMIND_PER_FILE``
     - ``true``
     - 逐文件执行 pipeline。
   * - ``REVIEWMIND_INLINE_REVIEW``
     - ``true``
     - 产出 inline ``suggestion`` 区块。
   * - ``REVIEWMIND_MAX_FINDINGS_PER_FILE``
     - ``10``
     - 每个文件最多保留几条 finding。
   * - ``REVIEWMIND_RAG_ENABLED``
     - ``true``
     - 整体 RAG 开关。
   * - ``REVIEWMIND_REMOTE_RAG``
     - ``true``
     - 用服务器端 ``/rag`` 而非在本地加载 FAISS（省 runner 内存）。
   * - ``REVIEWMIND_GATE_ON``
     - ``error``
     - 哪一级严重度会让 Check Run 变 ``failure``\ ：
       ``none`` / ``warning`` / ``error``\ 。
   * - ``REVIEWMIND_INCLUDE_CI_SIGNALS``
     - ``true``
     - 把失败 job 的末端日志前置到 diff。
   * - ``REVIEWMIND_RULES_DIR``
     - *(未设)*
     - Per-repo ``*.md`` 规则文件的路径。

完整变量与对应 CLI flag 在 :doc:`configuration` 与
:doc:`../reference/cli`。

Branch protection
-----------------

让 reviewer 真的能挡合并：

1. 跑至少一次 ``REVIEWMIND_GATE_ON=error`` 的 PR──PR 的 Checks 标签页就会出现
   ``reviewmind`` 这个 check。
2. 到 **Settings → Branches → branch protection rule**\ ，选你的 ``main``
   （或目标 branch）。
3. 启用 **Require status checks to pass before merging**\ ，把
   ``reviewmind`` 加进必需检查。

之后，只要 PR 还有至少一条 ``error`` 严重度的 finding 就无法合并，直到：

* 作者处理该 finding（并通过推新 commit 或重新触发来重跑）；或者
* Maintainer 强制覆盖该 check。

总结评论会显示 error / warning / info 的数量分布，作者就能直接看到是哪一级
踩到 gate。

让触发等待 CI 完成
------------------

默认的 ``pull_request`` trigger 推 commit 后马上跑。如果你想让 reviewer
等 CI 完成才跑（这样才能看到 CI 失败日志），改成：

.. code-block:: yaml

   on:
     workflow_run:
       workflows: ["CI"]
       types: [completed]

在 ``workflow_run`` 模式下要从 run payload 取得 PR 编号，请参考 GitHub
Actions 对 ``workflow_run`` context 的说明。

Self-hosted GPU runner（可选）
------------------------------

如果你想跳过远程服务器，直接在 runner 上跑推理，就需要一台有 CUDA GPU 的
self-hosted runner。\ ``ubuntu-latest``\ （GitHub-hosted）装不下 30B。

Workflow 范例：

.. code-block:: yaml

   jobs:
     reviewmind:
       runs-on: [self-hosted, gpu]
       env:
         REVIEWMIND_BACKEND: local
         REVIEWMIND_MODEL_NAME: Qwen/Qwen3-Coder-30B-A3B-Instruct
         REVIEWMIND_LORA_PATH: ../train/outputs-lora-qwen3-coder-30b
         REVIEWMIND_USE_REMOTE_PIPELINE: "false"
         REVIEWMIND_REMOTE_RAG: "false"
       steps:
         - uses: actions/checkout@v4
         - run: pip install -e ".[local]"
         - run: python -m reviewmind review-pr

flag 都一样，只是每个文件要 5-10 分钟（vs 配好的服务器上的约 30 秒）。
