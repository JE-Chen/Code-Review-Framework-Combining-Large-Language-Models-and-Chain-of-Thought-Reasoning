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

Python 版本
-----------

需要 Python ``>=3.12``\ ──套件用了 PEP 604 union 語法（\ ``str | None``\ ）
與 ``dataclass(slots=True, kw_only=True)`` 等較新模式。

GPU 注意事項
------------

* ``bitsandbytes`` 需要 CUDA。Windows 環境請使用上游
  ``bitsandbytes-windows-webui`` wheel，或直接在 WSL2 內執行。
* Qwen3-Coder-30B 模型載入時使用 4-bit NF4 量化（約 18 GB VRAM）。較小的
  LoRA 目標（Qwen3-1.7B、Qwen2.5-Coder-7B）可在單張 12 GB 卡上跑。

Embedding 模型
--------------

RAG 檢索使用 ``Qwen/Qwen3-Embedding-4B``\ （約 8 GB VRAM）。CI runner 上不要
載入它──請改用伺服器端的 ``/rag`` endpoint，詳見
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
