prthinker（繁體中文）
========================

為 GitHub、GitLab、Gitea 的 Pull／Merge Request 設計的思維鏈
（Chain-of-Thought）程式碼審查框架，底層由微調後的 Qwen3-Coder 模型加上
檢索增強（RAG）提示驅動。

``prthinker`` 會讀取 PR diff、執行五步思維鏈審查、把結構化的總結與
一鍵套用的 ``suggestion`` 區塊回貼到 PR。它會從每個 repo 的歷史中學習──
被 PR 作者拒絕的留言下次會被過濾掉，被採納的建議會以前例的形式注入下一輪
prompt──並且可以充當合併前的必要狀態檢查。

你會得到什麼
------------

* **五步 CoT pipeline**\ ──``first_summary`` → ``first_code_review`` →
  ``linter`` → ``code_smell`` → ``total_summary``\ ，外加可選的逐檔
  inline-findings 步驟，輸出結構化 JSON。
* **逐檔 inline review**\ ，搭配 GitHub ``suggestion`` 區塊。
* **全域 RAG + 各 repo 規則包**\ ：透過 ``--rules-dir`` 注入團隊規範。
* **兩份學習語料**\ ：\ ``dismissed.jsonl``\ （過濾重複命中）與
  ``accepted.jsonl``\ （top-K 範例注入 prompt）。
* **CI 失敗訊號**\ 前置到 diff，提供 grounded review。
* **合併前 Check Run gate**\ ──可設成必要狀態檢查。
* **可替換 backend**\ ：本機 in-process Qwen + LoRA，或 HTTP 遠端推論。
* **與 forge 無關的前端**\ ：GitHub、GitLab、Gitea 共用同一個
  ``PlatformAdapter``\ ；並內附可直接使用的 GitLab pipeline
  ``.gitlab-ci.yml``\ 。

.. toctree::
   :maxdepth: 2
   :caption: 使用指南

   guide/installation
   guide/quickstart
   guide/end-to-end-example
   guide/github-actions
   guide/gitlab-ci
   guide/configuration
   guide/repo-config

.. toctree::
   :maxdepth: 2
   :caption: 觀念

   concepts/architecture
   concepts/pipeline
   concepts/rag-and-rules
   concepts/corpora
   concepts/ci-and-gate
   concepts/cache-and-telemetry
   concepts/judge-and-streaming
   concepts/redaction-and-mcp
   concepts/hook-self-correct-auto-fix
   concepts/docker-platforms-report
   concepts/research-extensions

.. toctree::
   :maxdepth: 2
   :caption: 參考

   reference/cli
   reference/http-api
   reference/python-api

索引
----

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
