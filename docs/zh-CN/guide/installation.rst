安装
====

``prthinker`` 以 Python 包形式发布，提供三种安装 profile。根据代码
实际要跑的位置选一个即可。

安装 profile
------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Profile
     - 会装什么
   * - *(base)*
     - ``httpx``\ 、\ ``pydantic``\ ──只要能调用远程推理服务器、能对 GitHub
       发 REST 就够了。\ **CI runner 用这个**\ ，job 才会轻、才会快。
   * - ``runner``
     - 与 base 等价（在 workflow 里留个明确名字）。
   * - ``local``
     - ``transformers``\ 、\ ``torch``\ 、\ ``accelerate``\ 、\ ``bitsandbytes``\ 、
       ``peft``\ 、\ ``faiss-cpu``\ 、\ ``numpy``\ 。完整 pipeline 在本地跑时用
       这个──通常是 GPU 开发机。
   * - ``server``
     - 在 ``local`` 之上再加 ``fastapi`` 和 ``uvicorn``\ 。给推理服务器
       的机器用。

安装
----

从本 repo 的 checkout 中安装：

.. code-block:: bash

   # CI runner / 薄客户端
   pip install -e ".[runner]"

   # 本地开发（in-process 推理）
   pip install -e ".[local]"

   # 服务器（host /ask、/rag、/review）
   pip install -e ".[server]"

Python 版本
-----------

需要 Python ``>=3.12``\ ──包内用了 PEP 604 union 语法（\ ``str | None``\ ）
与 ``dataclass(slots=True, kw_only=True)`` 等较新模式。

GPU 注意事项
------------

* ``bitsandbytes`` 需要 CUDA。Windows 环境请使用上游
  ``bitsandbytes-windows-webui`` wheel，或直接在 WSL2 内运行。
* Qwen3-Coder-30B 模型加载时使用 4-bit NF4 量化（约 18 GB VRAM）。较小的
  LoRA 目标（Qwen3-1.7B、Qwen2.5-Coder-7B）可在单张 12 GB 卡上跑。

Embedding 模型
--------------

本机 RAG 检索默认使用 ``google/embeddinggemma-300m``\ （HF 上的 gated
repo──需先在模型页同意授权并设置 ``HF_TOKEN``\ ），通过
sentence-transformers 加载，校准后的 cosine 阈值为 0.32。设置
``EMB_MODEL=Qwen/Qwen3-Embedding-4B``\ （约 8 GB VRAM，阈值 0.7）可复现
旧版索引；随附的推理服务器本身即固定使用旧版模型。CI runner 上不要
加载 embedding 模型──请改用服务器端的 ``/rag`` endpoint，详见
:doc:`../concepts/rag-and-rules`。

验证安装
--------

.. code-block:: bash

   # CLI 应该能回 subcommand 说明
   prthinker --help

   # 五个内置 CoT step 应该都注册好
   python -c "from prthinker.steps import registered_steps; \
              print([s.name for s in registered_steps()])"

预期输出::

   ['first_summary', 'first_code_review', 'linter', 'code_smell', 'total_summary']
