安裝
====

``prthinker`` 以 Python 套件形式發佈，提供三種安裝 profile。依照
程式碼實際要跑的位置挑一個即可。

安裝 profile
------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Profile
     - 會裝什麼
   * - *(base)*
     - ``httpx``\ 、\ ``pydantic``\ ──只要能呼叫遠端推論伺服器、能對 GitHub
       發 REST 就夠了。\ **CI runner 用這個**\ ，job 才會輕、才會快。
   * - ``runner``
     - 與 base 等價（在 workflow 裡留個明確名字）。
   * - ``local``
     - ``transformers``\ 、\ ``torch``\ 、\ ``accelerate``\ 、\ ``bitsandbytes``\ 、
       ``peft``\ 、\ ``faiss-cpu``\ 、\ ``numpy``\ 。完整 pipeline 在本機跑時用
       這個──通常是 GPU 開發機。
   * - ``server``
     - 在 ``local`` 之上再加 ``fastapi`` 與 ``uvicorn``\ 。給推論伺服器
       的機器用。

安裝
----

從本 repo 的 checkout 中安裝：

.. code-block:: bash

   # CI runner / 薄客戶端
   pip install -e ".[runner]"

   # 本機開發（in-process 推論）
   pip install -e ".[local]"

   # 伺服器（host /ask、/rag、/review）
   pip install -e ".[server]"

鎖定環境
--------

若要 bit-for-bit 可重現的安裝（CI 在每個 PR 上跑的就是這套），請改用
``requirements/`` 下以 hash 鎖定的 requirement 檔，不要讓 pip 重新解析
相依：

.. code-block:: bash

   # Runner profile，精確 pin 住並以 hash 驗證的 wheels
   pip install --require-hashes -r requirements/runner.lock
   pip install -e . --no-deps

   # 完整 CI 工具鏈（pytest、ruff、bandit、build、twine）
   pip install --require-hashes -r requirements/ci.lock
   pip install -e . --no-deps

``runner.in`` / ``ci.in`` 是人工編輯的輸入檔；相依有變動時用
``pip-compile --generate-hashes`` 重新產生 lock（見
``requirements/README.md``\ ）。GPU 伺服器則維持 image-locked ──
PyTorch / CUDA wheel 因平台而異，其 Dockerfile 與 image digest 才是
可重現性的邊界。

Python 版本
-----------

需要 Python ``>=3.12``\ ──套件用了 PEP 604 union 語法（\ ``str | None``\ ）
與 ``dataclass(slots=True, kw_only=True)`` 等較新模式。

GPU 注意事項
------------

* bf16 家族模型（\ ``Qwen3-Coder-30B-A3B``\ 、\ ``Qwen3-30B-A3B``\ 、
  ``gemma-4-31B-it``\ ）以純 **bf16** 載入，並用平衡的
  ``device_map="auto"`` 切分──30B MoE base 在兩張 46 GB 卡上約各佔
  28 GB，掛上未合併的 LoRA 後每卡約 36–38 GB。這些模型完全不經過
  bitsandbytes；在頻寬受限的單卡部署上可設 ``PRTHINKER_QUANT=fp8``
  改用 FP8 權重。
* 其他模型名稱預設走 8-bit bitsandbytes 量化。``bitsandbytes`` 需要
  CUDA；Windows 環境請使用上游 ``bitsandbytes-windows-webui`` wheel，
  或直接在 WSL2 內執行。較小的 LoRA 目標（Qwen3-1.7B、Qwen2.5-Coder-7B）
  可在單張 12 GB 卡上跑。

Embedding 模型
--------------

本機 RAG 檢索預設使用 ``google/embeddinggemma-300m``\ （HF 上的 gated
repo──需先在模型頁同意授權並設定 ``HF_TOKEN``\ ），透過
sentence-transformers 載入，校準後的 cosine 門檻為 0.32。設定
``EMB_MODEL=Qwen/Qwen3-Embedding-4B``\ （約 8 GB VRAM，門檻 0.7）可重現
舊版索引；隨附的推論伺服器本身即固定使用舊版模型。CI runner 上不要
載入 embedding 模型──請改用伺服器端的 ``/rag`` endpoint，詳見
:doc:`../concepts/rag-and-rules`。

驗證安裝
--------

.. code-block:: bash

   # CLI 應該能回 subcommand 說明
   prthinker --help

   # 五個內建 CoT step 應該都註冊好
   python -c "from prthinker.steps import registered_steps; \
              print([s.name for s in registered_steps()])"

預期輸出::

   ['first_summary', 'first_code_review', 'linter', 'code_smell', 'total_summary']
