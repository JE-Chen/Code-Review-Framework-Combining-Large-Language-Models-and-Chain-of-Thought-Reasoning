Docker、多平台、縱向報告
========================

三項把 prthinker 從「可被 import 的函式庫」升級為「可營運的系統」之
新增：

* **Docker compose**\ ──一指令自架部署。
* **PlatformAdapter**\ ──GitHub 與 GitLab 共用一個 Strategy 介面。
* **``prthinker report``**\ ──跨 store 縱向匯總。

以 Docker compose 自架部署
--------------------------

``docker/`` 目錄下之 bundle 一指令即可部署 FastAPI 推論伺服器，預設直接
exposed 在 port ``9000`` 上。base compose 之上可再疊兩個 overlay：\
**TLS overlay** 以 nginx 做 TLS termination + bearer-token 驗證；\
**monitoring overlay** 再加上 Prometheus + Grafana + DCGM（GPU）+
cAdvisor（容器），全部藏在單一 nginx reverse proxy 後面。兩項主機需求
（使用 TLS overlay 才需要 TLS 憑證）：

* NVIDIA GPU 加上與設定之 CUDA 版本相容之驅動（預設 ``13.0.1``\ ）。
* Docker 24+ 並配置 NVIDIA container runtime（\ ``docker-compose.server-qwen3-coder.yml``
  內 ``runtime: nvidia``\ ）。
* （TLS overlay 才需）TLS 憑證（Let's Encrypt 或 self-signed），mount
  進 nginx container。

檔案清單：

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - 檔案
     - 用途
   * - ``docker/Dockerfile.server-qwen3-coder``
     - Qwen3-Coder-30B image：CUDA-runtime base + Python 3.12 +
       ``pip install -e .[server]``\ 。模型權重\ **不**\ 烤進 image，於首次
       執行時拉到 volume 中。
   * - ``docker/docker-compose.server-qwen3-coder.yml``
     - 可攜的 Qwen3-Coder-30B 部署：單一 service（\ ``prthinker``\ ），exposed 在
       ``${PRTHINKER_HOST_PORT:-9000}``\ ；兩個 volume（\ ``hf_cache``\ 、
       ``data``\ ）。HTTP only，無 TLS\ 。
   * - ``docker/Dockerfile.server-gemma4`` +
       ``docker/docker-compose.server-gemma4.yml``
     - 本機 DGX Spark 上目前的 Gemma-4-31B-it 部署（NGC PyTorch base、
       ``transformers>=5.10``\ 、程式碼以 bind-mount 掛入）。見
       ``READMEs/local_gemma_deployment.md``\ ；下方 TLS / monitoring
       overlay 僅對應 Qwen3-Coder compose\ 。
   * - ``docker/docker-compose.tls.yml``
     - 可選 TLS overlay：加上 ``nginx`` service 做 TLS + bearer-token
       驗證，把 ``prthinker`` 藏在內網後面（nginx 預設在 host ``443``\ ）\ 。
   * - ``docker/nginx.conf``
     - TLS overlay 使用\ 。TLS termination；\ ``/healthz`` 不檢查 auth，
       其他路徑要求 ``Authorization: Bearer <PRTHINKER_BACKEND_TOKEN>``\ 。
   * - ``docker/entrypoint-nginx.sh``
     - TLS overlay 使用\ 。container 啟動時把 token 注入 ``nginx.conf``\ ；
       env 變數缺失時拒絕啟動（fail-fast）\ 。
   * - ``docker/docker-compose.monitoring.yml``
     - 可選 monitoring overlay：加上 ``prometheus``\ 、\ ``grafana``\ 、
       ``dcgm-exporter``\ （GPU 指標）、\ ``cadvisor``\ （容器指標），
       以及一個占用 host ``9000`` 的 ``nginx`` reverse proxy，依路徑把所有
       儀表板收斂到同一個 port\ 。
   * - ``docker/monitoring/nginx.conf``
     - monitoring overlay 使用\ 。依路徑分流 ``/grafana/``\ 、
       ``/prometheus/``\ 、\ ``/cadvisor/`` 與靜態 ``/kg/`` repo
       knowledge-graph 頁；其餘一律 proxy 給 ``prthinker``\ 。
   * - ``docker/monitoring/prometheus.yml``
     - monitoring overlay 之 scrape 設定（prthinker ``/metrics``\ 、
       DCGM、cAdvisor）\ 。
   * - ``docker/monitoring/grafana/``
     - 預先佈建之 Grafana datasource 與 ``prthinker-overview`` 儀表板，
       首次啟動自動載入\ 。
   * - ``docker/rebuild-server.sh``
     - 不含 flash-attn / transformers pin 重建 server image 之 helper
       （本 repo 支援之 bf16 + SDPA 部署）\ 。
   * - ``docker/.env.example``
     - host port、CUDA tag 範本，以及可選之 TLS overlay 用 bearer token /
       TLS 憑證目錄、monitoring overlay 用 Grafana 管理帳密\ 。

啟動（預設 — HTTP on :9000）：

.. code-block:: bash

   cd docker
   cp .env.example .env       # PRTHINKER_HOST_PORT 預設 9000
   docker compose -f docker-compose.server-qwen3-coder.yml up -d

   # 驗證
   curl http://your-host:9000/healthz

啟動（overlay — TLS + bearer token on :443）：

.. code-block:: bash

   cd docker
   # 編輯 .env：
   #   PRTHINKER_BACKEND_TOKEN=$(openssl rand -hex 32)
   #   TLS_CERT_DIR=/etc/letsencrypt/live/your-host
   docker compose -f docker-compose.server-qwen3-coder.yml -f docker-compose.tls.yml up -d

   curl https://your-host/healthz \
       -H "Authorization: Bearer $PRTHINKER_BACKEND_TOKEN"

啟動（monitoring overlay — 儀表板 on :9000）：

.. code-block:: bash

   cd docker
   # .env 可選：
   #   GRAFANA_ADMIN_USER=admin
   #   GRAFANA_ADMIN_PASSWORD=$(openssl rand -hex 16)
   docker compose -f docker-compose.server-qwen3-coder.yml -f docker-compose.monitoring.yml up -d

   # 全部收在單一 host port（預設 9000）後面：
   curl http://your-host:9000/healthz          # prthinker
   #   開 http://your-host:9000/grafana/        # Grafana（預設 admin / admin）

monitoring overlay 之 nginx 占用 host ``9000`` 並依路徑分流，因此單一對外
port（或一個上游 proxy / Cloudflare tunnel）即可同時 expose 伺服器與所有
儀表板：

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - URL 路徑（host ``9000`` 之下）
     - 提供
   * - ``/healthz``\ 、\ ``/review/*``\ 、\ ``/ask/*``\ 、\ ``/metrics``\ …
     - prthinker FastAPI 伺服器（未被下列規則命中之路徑）\ 。
   * - ``/grafana/``
     - Grafana UI——自動佈建之 ``prthinker-overview`` 儀表板。預設登入
       ``admin`` / ``admin``\ （以 ``GRAFANA_ADMIN_USER`` /
       ``GRAFANA_ADMIN_PASSWORD`` 覆寫）\ 。
   * - ``/prometheus/``
     - Prometheus UI / query API（保留 30 天）\ 。
   * - ``/cadvisor/``
     - cAdvisor 容器資源 UI\ 。
   * - ``/kg/``
     - 由 ``.prthinker/`` 渲染之靜態 repo knowledge-graph 頁\ 。多 repo
       部署另有 per-repo 頁 ``/kg/<name>/``\ （nginx route 比對
       ``[A-Za-z0-9._-]+``\ ），單一主機可為每個被審 repo 各供一份
       knowledge graph\ 。

DCGM GPU 指標 exporter 無對外路徑——只由 Prometheus 在內網 docker network
上 scrape。TLS 與 monitoring overlay 都會占用 host ``9000``/nginx，請透過
上游 proxy 整合，不要三個 compose 檔同時疊用\ 。

monitoring overlay 觀測什麼
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Prometheus scrape 四個 job——``prthinker-fastapi``\ （\ ``/metrics``
endpoint）、\ ``dcgm-gpu``\ （各 GPU 遙測）、\ ``cadvisor-containers``\
（各容器資源用量）與 ``prometheus-self``\ ——並保留 30 天歷史。預先佈建之
``prthinker-overview`` Grafana 儀表板把它們渲染為十四個 panel：

* **服務**\ ──各 endpoint 請求率、延遲 p50 / p95 / p99、HTTP 5xx 率
  （來自 FastAPI ``/metrics`` histogram）\ 。
* **審查**\ ──完成審查率（依 outcome）、審查耗時 p50 / p95、進行中審查數、
  每次審查平均 findings（來自伺服器每跑完一次審查就輸出之
  ``prthinker_reviews_total`` / ``prthinker_review_duration_seconds`` /
  ``prthinker_review_findings`` / ``prthinker_reviews_in_progress``
  series——所以 HTTP 流量閒置時儀表板仍有審查資料）\ 。
* **GPU**\ ──使用率、已用記憶體、功耗、溫度（來自 DCGM）\ 。
* **容器**\ ──prthinker CPU cores、RAM、網路 RX/TX（來自 cAdvisor）\ 。

alerting 規則隨附於 ``monitoring/alerts.yml``\ （經 ``prometheus.yml`` 之
``rule_files`` 載入)——backend 掛掉、5xx 超過 5%、審查 p95 超過 10 分鐘、
審查錯誤、GPU 超過 85 °C。它們會以 ``ALERTS`` series 顯示在 Prometheus UI
與 Grafana；需要路由/呼叫請加一個 Alertmanager(於 ``prometheus.yml`` 加
``alerting:`` 區塊指向它)。門檻請依流量與 SLO 自行調整\ 。

安全重建 image（``rebuild-server.sh``）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在 GPU 主機上直接 ``docker compose build``\ ，build 之峰值 RAM 可能與
執行中之模型容器相撞而觸發 kernel OOM-killer——而它往往先殺
``cloudflared`` / ``sshd``\ ，表現為「GPU 伺服器 build 到一半斷線」。
``docker/rebuild-server.sh`` 把安全流程編進去：停掉模型容器釋出其 host
RAM、pull 最新 ``Dockerfile.server-qwen3-coder``\ 、build 時每 2 秒快照 ``free -h``\ 、
build 後掃 ``dmesg`` 找 OOM-killer 指紋，再把伺服器拉回並阻塞到
``/healthz`` 回 200 且 boot guard 確認非 eager attention impl。小主機請
降低 build 並行度：

.. code-block:: bash

   ./docker/rebuild-server.sh                       # 預設 MAX_JOBS=16
   FLASH_ATTN_MAX_JOBS=4 ./docker/rebuild-server.sh # <= 128 GiB RAM 主機

Volume 說明：

* ``hf_cache``\ ──HuggingFace 權重。\ ``docker compose down`` 不會清除；
  只在換模型且想釋出約 80 GB 空間時才刪。
* ``data``\ ──cache.sqlite、telemetry.sqlite、dismissed.jsonl、
  accepted.jsonl，請納入備份。
* TLS 目錄為 **host bind-mount**\ ，憑證更新與 compose 生命週期分開管。
* ``prometheus_data`` / ``grafana_data``\ （僅 monitoring overlay）──
  指標歷史與 Grafana 狀態；想重置儀表板可安全刪除\ 。

Image 刻意不烤入權重——image 重建不應作廢 ~80 GB 下載。代價是
``docker compose up`` 首次請求要等權重下載；後續即熱。

以 ``PlatformAdapter`` 支援多平台
---------------------------------

Pipeline 透過一個 Strategy 介面同時對接 GitHub 與 GitLab：

.. code-block:: text

   prthinker.platforms.base.PlatformAdapter        (ABC)
       │
       ├── GitHubAdapter   (包住 github_api.py + checks.py)
       └── GitLabAdapter   (直接以 httpx 打 /api/v4)

每個 adapter 必實作之五個方法：

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
     - auto-fix 開 draft PR 時用。
   * - ``upsert_summary_comment(body)``
     - 以 ``comment_marker`` 子字串 upsert 之留言。
   * - ``submit_inline_review(findings, summary_body, event)``
     - inline comment 含可選 ``suggestion`` 區塊；\ ``event`` 對應到
       GitHub Review verb 或 GitLab discussion 前綴。
   * - ``open_gate(head_sha)`` / ``close_gate(handle, result)``
     - GitHub：Check Run。GitLab：commit status，呼叫
       ``POST /projects/:id/statuses/:sha``\ 。

adapter 掩蓋之 wire-format 差異
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 28 36 36

   * - 面向
     - GitHub
     - GitLab
   * - 識別子
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
     - discussions 無原生 verb；body 加前綴
       ``**Verdict: APPROVE**``\ ，並把判定鏡射到 approvals API
       （APPROVE 時呼叫 ``POST /merge_requests/:iid/approve``\ ，
       REQUEST_CHANGES 時呼叫 ``/unapprove``\ ，best-effort）
   * - 驗證 header
     - ``Authorization: Bearer <token>``
     - ``PRIVATE-TOKEN: <token>``

CLI 用法
~~~~~~~~

.. code-block:: bash

   # GitHub（預設）
   prthinker review-pr --repo owner/name --pr-number 42

   # gitlab.com 上之 GitLab
   prthinker review-pr \
       --platform gitlab \
       --repo group/project \
       --pr-number 42 \
       --github-token "$GITLAB_TOKEN"

   # 自架之 GitHub Enterprise
   prthinker review-pr \
       --platform github \
       --platform-base-url https://github.example.com/api/v3 \
       --repo owner/name --pr-number 42

``--github-token`` flag 也接受 ``GITLAB_TOKEN`` 作 fallback；CLI 依
``--platform`` 自動判斷該讀哪個。\ ``--repo`` 也接受 GitLab CI 之
``CI_PROJECT_PATH``\ 。

GitLab 上之平台附加功能
~~~~~~~~~~~~~~~~~~~~~~~

過去僅支援 GitHub 之兩項功能改經 adapter 解析，GitLab 亦已實作：

* **CI 訊號注入**\ （\ ``--include-ci-signals``\ ）──GitHub 讀
  Actions 之 ``/jobs/:id/logs``\ ；GitLab 讀 pipeline job trace
  （\ ``/projects/:id/jobs/:id/trace``\ ）。
* **Auto-fix**\ （\ ``--auto-fix-threshold``\ ）──GitHub 以 pulls API
  開草稿 PR；GitLab 以 Merge Requests API 開 ``Draft:`` MR。

兩者皆無之平台（如 Gitea）仍優雅降級──記 log 跳過，絕不 crash。
其他功能（CoT pipeline、gate、inline review、judge、self-correct）
GitHub 與 GitLab 皆支援。

``prthinker report``\ ──縱向匯總
---------------------------------

框架寫入之四份 store（telemetry SQLite、cache SQLite、dismissed /
accepted JSONL）會悄悄累積。\ ``prthinker report`` 把它們 join 起來，
產出可給人或機器讀之匯總：

.. code-block:: bash

   # markdown 到 stdout
   prthinker report --since-days 30

   # html 檔，方便寄給 ops
   prthinker report --since-days 30 --format html --out report.html

   # json 可接 Grafana / DuckDB
   prthinker report --since-days 30 --format json --out report.json

渲染之段落：

1. **依 (backend, model) 之使用量**\ ──calls、cache hits、in/out
   tokens、USD 成本、p50 / p95 延遲。
2. **Cache**\ ──entry 數 + lifetime 命中數。
3. **每日成本 sparkline**\ ──最近 14 天之 ASCII 條，含峰值標注。
4. **Dismissed corpus**\ ──總數 + 各 reason 之筆數
   （\ ``thumbs-down reaction`` / ``reply matched: ...``\ ）。
5. **Accepted corpus**\ ──總數 + 採納數前 5 之檔案。

實作性質：

* **純 stdlib + 既有套件模組**\ ；無 numpy、無 matplotlib──sparkline
  用八種 Unicode block：\ ``▁▂▃▄▅▆▇█``\ 。
* **缺檔不會 error**\ 。telemetry 或某 JSONL 尚未存在時，該段落顯示
  「無資料」，其餘段落照常。
* **唯讀**\ 。每個 store 都以 read mode 開啟，跑 report 不會修改任何
  狀態。

各格式適用情境
~~~~~~~~~~~~~~

* ``markdown``\ ──貼到 wiki 或 commit 進 repo 作 weekly 標題。
* ``html``\ ──單檔 self-contained，可放 static server 或 email。
* ``json``\ ──餵下游工具（DuckDB、Grafana JSON datasource、ad-hoc
  pandas）。

目前不做語義 clustering
~~~~~~~~~~~~~~~~~~~~~~~

目前 report 不對 dismissed comments 做語義 cluster。Dismissed store 之
embedding 是 server 啟動時為 filter 計算的；單為 cluster 幾百筆留言而把
embedding 模型也搬進 runner 不划算。若日後需要 cluster，請以
``--format json`` 為對接介面，自選 embedding + KMeans 套件處理。
