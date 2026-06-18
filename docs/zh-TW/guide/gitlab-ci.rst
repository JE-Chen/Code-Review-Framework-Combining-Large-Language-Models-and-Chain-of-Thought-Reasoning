GitLab CI 整合
==============

審查器是\ **與 forge 無關（forge-agnostic）**\ 的：同一支 runner CLI
(``python -m prthinker review-pr``) 透過單一
:class:`~prthinker.platforms.base.PlatformAdapter` 策略,即可驅動 GitHub、
GitLab 或 Gitea 的 merge request,用 ``--platform``\ （或
``$PRTHINKER_PLATFORM``\ ）選擇。專案已內附可直接使用的 GitLab pipeline,
位於 repo 根目錄的 ``.gitlab-ci.yml``\ 。

如何對應到 GitLab
-----------------

審查路徑裡沒有任何 GitHub 專屬的東西。CLI 會自動解析 GitLab-CI 的環境變數,
因此 pipeline 不必傳任何識別參數:

.. list-table::
   :header-rows: 1
   :widths: 38 27 35

   * - GitLab-CI 變數
     - CLI 參數
     - 意義
   * - ``$CI_PROJECT_PATH``
     - ``--repo``
     - ``group/project`` 路徑
   * - ``$CI_MERGE_REQUEST_IID``
     - ``--pr-number``
     - merge request 的 iid
   * - ``$GITLAB_TOKEN``
     - ``--github-token``
     - API token（需 ``api`` scope）
   * - ``$PRTHINKER_PLATFORM=gitlab``
     - ``--platform``
     - 選用 GitLab adapter

adapter 會把總結貼成 merge-request note、把 findings 貼成 diff 上的
inline 討論串,並把 gate 設成名為 ``prthinker`` 的 commit status──
這就是 GitHub Check Run 在 GitLab 的對應物。

單一 job,沒有 matrix
---------------------

和 GitHub Actions workflow 不同,這裡沒有 ``enumerate``\ ／matrix／
``aggregate`` 的拆分。那套 fan-out 只是為了把單一共享 GPU backend
分流到逐檔 runner 上。``review-pr`` 會在同一個行程裡審查所有變更檔,
並直接貼出總結、inline 討論與 gate,所以 GitLab pipeline 就是一個
``review-pr`` job。

需要的 CI/CD 變數
-----------------

在 **Settings → CI/CD → Variables** 設定以下變數（token 請勾選
\ *Masked*\ ）:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - 變數
     - 用途
   * - ``GITLAB_TOKEN``
     - 具 ``api`` scope 的 Project／Group access token 或 PAT。內建的
       ``CI_JOB_TOKEN`` 無法貼 merge-request note。
   * - ``PRTHINKER_BACKEND_URL``
     - 推論 backend 的 HTTPS URL;CI runner 本身不需要 GPU。
   * - ``PRTHINKER_BACKEND_API_KEY``
     - backend 的 bearer token（選用）。

Pipeline 檔案
-------------

內附的 ``.gitlab-ci.yml`` 精簡成單一 job,核心形狀如下:

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

``rules`` 子句對應 GitHub 的 ``pull_request`` 觸發:此 job 只在
merge-request pipeline 上執行。

擋下合併
--------

gate 是 ``prthinker`` 這個 commit status,而不是 pipeline 本身的成功／
失敗。要硬性擋下合併,請在 **Settings → Merge requests**\ （merge checks）
或受保護分支規則裡「要求該狀態通過」──這與 GitHub 要求 Check Run
的模式相同。總結 note 會列出 error／warning／info 的數量,作者一眼就能
看出是什麼觸發了 gate。

功能對等
--------

審查本身──CoT pipeline、RAG、學習語料、inline suggestion 與 gate──
在各 forge 之間完全相同。有兩個 GitHub 專屬的附加功能在 GitLab 上會優雅
降級（記錄一行後跳過,絕不會 crash）:CI 失敗訊號前置,以及 auto-fix
草稿 PR。

自架（self-hosted）GitLab 只要用 ``--platform-base-url``\ （或
``$PRTHINKER_PLATFORM_BASE_URL``\ ）把 adapter 指向你的實例 API 即可,
例如 ``https://gitlab.example.com/api/v4``\ 。同樣的方式搭配
``--platform gitea`` 即可服務 Gitea。
