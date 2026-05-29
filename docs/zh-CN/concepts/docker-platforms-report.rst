Docker、多平台、纵向报告
========================

三项把 prthinker 从「可被 import 的库」升级为「可运营的系统」之新增：

* **Docker compose**\ ──一指令自部署。
* **PlatformAdapter**\ ──GitHub 与 GitLab 共用一个 Strategy 接口。
* **``prthinker report``**\ ──跨 store 纵向汇总。

以 Docker compose 自部署
------------------------

``docker/`` 目录下之 bundle 一指令即可部署 FastAPI 推理服务器，默认直接
exposed 在 port ``9000`` 上。正式部署可叠用 TLS overlay，加上 nginx 做
TLS termination + bearer-token 认证。两项主机需求（使用 overlay 才需要
TLS 证书）：

* NVIDIA GPU 加上与设置之 CUDA 版本兼容之驱动（默认 ``12.2.0``\ ）。
* Docker 24+ 并配置 NVIDIA container runtime（\ ``docker-compose.yml``
  内 ``runtime: nvidia``\ ）。
* （Overlay 才需）TLS 证书（Let's Encrypt 或 self-signed），mount 进
  nginx container。

文件清单：

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - 文件
     - 用途
   * - ``docker/Dockerfile.server``
     - CUDA-runtime base + Python 3.12 + ``pip install -e .[server]``\ 。
       模型权重\ **不**\ 烤进 image，于首次运行时拉到 volume 中。
   * - ``docker/docker-compose.yml``
     - 默认部署：单一 service（\ ``prthinker``\ ），exposed 在
       ``${PRTHINKER_HOST_PORT:-9000}``\ ；两个 volume（\ ``hf_cache``\ 、
       ``data``\ ）。HTTP only，无 TLS\ 。
   * - ``docker/docker-compose.tls.yml``
     - 可选 overlay：加上 ``nginx`` service 做 TLS + bearer-token 认证，
       把 ``prthinker`` 藏在内网后面\ 。
   * - ``docker/nginx.conf``
     - Overlay 使用\ 。TLS termination；\ ``/healthz`` 不检查 auth，
       其他路径要求 ``Authorization: Bearer <PRTHINKER_BACKEND_TOKEN>``\ 。
   * - ``docker/entrypoint-nginx.sh``
     - Overlay 使用\ 。container 启动时把 token 注入 ``nginx.conf``\ ；
       env 变量缺失时拒绝启动（fail-fast）\ 。
   * - ``docker/.env.example``
     - host port、CUDA tag 模板，以及可选之 overlay 用 bearer token /
       TLS 证书目录\ 。

启动（默认 — HTTP on :9000）：

.. code-block:: bash

   cd docker
   cp .env.example .env       # PRTHINKER_HOST_PORT 默认 9000
   docker compose up -d

   # 验证
   curl http://your-host:9000/healthz

启动（overlay — TLS + bearer token on :443）：

.. code-block:: bash

   cd docker
   # 编辑 .env：
   #   PRTHINKER_BACKEND_TOKEN=$(openssl rand -hex 32)
   #   TLS_CERT_DIR=/etc/letsencrypt/live/your-host
   docker compose -f docker-compose.yml -f docker-compose.tls.yml up -d

   curl https://your-host/healthz \
       -H "Authorization: Bearer $PRTHINKER_BACKEND_TOKEN"

Volume 说明：

* ``hf_cache``\ ──HuggingFace 权重。\ ``docker compose down`` 不会清除；
  只在换模型且想释出约 80 GB 空间时才删。
* ``data``\ ──cache.sqlite、telemetry.sqlite、dismissed.jsonl、
  accepted.jsonl，请纳入备份。
* TLS 目录为 **host bind-mount**\ ，证书更新与 compose 生命周期分开管。

Image 刻意不烤入权重——image 重建不应作废 ~80 GB 下载。代价是
``docker compose up`` 首次请求要等权重下载；后续即热。

以 ``PlatformAdapter`` 支持多平台
---------------------------------

Pipeline 通过一个 Strategy 接口同时对接 GitHub 与 GitLab：

.. code-block:: text

   prthinker.platforms.base.PlatformAdapter        (ABC)
       │
       ├── GitHubAdapter   (包住 github_api.py + checks.py)
       └── GitLabAdapter   (直接以 httpx 打 /api/v4)

每个 adapter 必实现之五个方法：

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - 方法
     - 用途
   * - ``fetch_diff()``
     - 取得 PR / MR 之 unified diff。
   * - ``fetch_head_sha()``
     - head commit SHA──gate 需要。
   * - ``fetch_base_branch()``
     - auto-fix 开 draft PR 时用。
   * - ``upsert_summary_comment(body)``
     - 以 ``comment_marker`` 子串 upsert 之评论。
   * - ``submit_inline_review(findings, summary_body, event)``
     - inline comment 含可选 ``suggestion`` 区块；\ ``event`` 对应到
       GitHub Review verb 或 GitLab discussion 前缀。
   * - ``open_gate(head_sha)`` / ``close_gate(handle, result)``
     - GitHub：Check Run。GitLab：commit status，调用
       ``POST /projects/:id/statuses/:sha``\ 。

adapter 隐藏之 wire-format 差异
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 28 36 36

   * - 面向
     - GitHub
     - GitLab
   * - 标识符
     - ``owner/name`` + ``pr_number``
     - ``group/project`` URL-encoded + ``mr_iid``
   * - inline comment
     - ``POST /pulls/:n/reviews``\ ，\ ``comments[].line``
     - ``POST /merge_requests/:iid/discussions``\ ，\ ``position``
       （\ ``base_sha`` / ``start_sha`` / ``head_sha`` /
       ``new_path`` / ``new_line``\ ）
   * - status check
     - Check Run（\ ``POST /check-runs``\ ）
     - commit status（\ ``POST /statuses/:sha``\ ，
       ``state=pending|success|failed``\ ）
   * - review verdict
     - 原生 ``event: APPROVE`` / ``REQUEST_CHANGES`` / ``COMMENT``
     - GitLab discussions 无原生 verb，于 body 加前缀
       ``**Verdict: APPROVE**``\ （未来工作：APPROVE 时实际调用
       ``POST /merge_requests/:iid/approve``\ ）
   * - 鉴权 header
     - ``Authorization: Bearer <token>``
     - ``PRIVATE-TOKEN: <token>``

CLI 用法
~~~~~~~~

.. code-block:: bash

   # GitHub（默认）
   prthinker review-pr --repo owner/name --pr-number 42

   # gitlab.com 上之 GitLab
   prthinker review-pr \
       --platform gitlab \
       --repo group/project \
       --pr-number 42 \
       --github-token "$GITLAB_TOKEN"

   # 自部署之 GitHub Enterprise
   prthinker review-pr \
       --platform github \
       --platform-base-url https://github.example.com/api/v3 \
       --repo owner/name --pr-number 42

``--github-token`` flag 也接受 ``GITLAB_TOKEN`` 作 fallback；CLI 依
``--platform`` 自动判断该读哪个。\ ``--repo`` 也接受 GitLab CI 之
``CI_PROJECT_PATH``\ 。

目前仅支持 GitHub 之功能
~~~~~~~~~~~~~~~~~~~~~~~~

两处仍直打 GitHub Actions API，在 GitLab 上会以一行 log 跳过：

* **CI 信号注入**\ （\ ``--include-ci-signals``\ ）──用 Actions 之
  ``/jobs/:id/logs``\ 。GitLab 对应为
  ``/projects/:id/jobs/:id/trace``\ ，已列入未来工作。
* **Auto-fix draft PR**\ （\ ``--auto-fix-threshold``\ ）──用 GitHub
  pulls API 建立修补 PR；GitLab 对应为 Merge Requests API。

其他功能（CoT pipeline、gate、inline review、judge、self-correct）
GitHub 与 GitLab 皆支持。

``prthinker report``\ ──纵向汇总
---------------------------------

框架写入之四份 store（telemetry SQLite、cache SQLite、dismissed /
accepted JSONL）会悄悄积累。\ ``prthinker report`` 把它们 join 起来，
产出可给人或机器读之汇总：

.. code-block:: bash

   # markdown 到 stdout
   prthinker report --since-days 30

   # html 文件，方便寄给 ops
   prthinker report --since-days 30 --format html --out report.html

   # json 可接 Grafana / DuckDB
   prthinker report --since-days 30 --format json --out report.json

渲染之段落：

1. **依 (backend, model) 之使用量**\ ──calls、cache hits、in/out
   tokens、USD 成本、p50 / p95 延迟。
2. **Cache**\ ──entry 数 + lifetime 命中数。
3. **每日成本 sparkline**\ ──最近 14 天之 ASCII 条，含峰值标注。
4. **Dismissed corpus**\ ──总数 + 各 reason 之条数
   （\ ``thumbs-down reaction`` / ``reply matched: ...``\ ）。
5. **Accepted corpus**\ ──总数 + 采纳数前 5 之文件。

实现性质：

* **纯 stdlib + 既有包模块**\ ；无 numpy、无 matplotlib──sparkline
  用八种 Unicode block：\ ``▁▂▃▄▅▆▇█``\ 。
* **缺文件不会 error**\ 。telemetry 或某 JSONL 尚未存在时，该段落显示
  「无数据」，其余段落照常。
* **只读**\ 。每个 store 都以 read mode 打开，跑 report 不会修改任何
  状态。

各格式适用场景
~~~~~~~~~~~~~~

* ``markdown``\ ──贴到 wiki 或 commit 进 repo 作 weekly 标题。
* ``html``\ ──单文件 self-contained，可放 static server 或 email。
* ``json``\ ──喂下游工具（DuckDB、Grafana JSON datasource、ad-hoc
  pandas）。

目前不做语义 clustering
~~~~~~~~~~~~~~~~~~~~~~~

目前 report 不对 dismissed comments 做语义 cluster。Dismissed store 之
embedding 是 server 启动时为 filter 计算的；单为 cluster 几百条评论而把
embedding 模型也搬进 runner 不划算。若日后需要 cluster，请以
``--format json`` 为对接接口，自选 embedding + KMeans 包处理。
