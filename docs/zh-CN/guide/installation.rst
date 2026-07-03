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

锁定环境
--------

若要 bit-for-bit 可复现的安装（CI 在每个 PR 上跑的就是这套），请使用
``requirements/`` 下带 hash 锁定的 requirement 文件，而不是让 pip
重新解析依赖：

.. code-block:: bash

   # Runner profile，逐一经 hash 校验的精确 pinned wheel
   pip install --require-hashes -r requirements/runner.lock
   pip install -e . --no-deps

   # 完整 CI 工具链（pytest、ruff、bandit、build、twine）
   pip install --require-hashes -r requirements/ci.lock
   pip install -e . --no-deps

``runner.in`` / ``ci.in`` 是人工编辑的输入；依赖变动时用
``pip-compile --generate-hashes`` 重新生成 lock 文件（见
``requirements/README.md``\ ）。GPU 服务器则维持 image 锁定──
PyTorch / CUDA wheel 依平台而异，它的 Dockerfile 与 image digest
就是可复现性的边界。

Python 版本
-----------

需要 Python ``>=3.12``\ ──包内用了 PEP 604 union 语法（\ ``str | None``\ ）
与 ``dataclass(slots=True, kw_only=True)`` 等较新模式。

GPU 注意事项
------------

* bf16 家族模型（\ ``Qwen3-Coder-30B-A3B``\ 、\ ``Qwen3-30B-A3B``\ 、
  ``gemma-4-31B-it``\ ）以纯 **bf16** 加载，并做均衡的
  ``device_map="auto"`` 切分──30B MoE base 在两张 46 GB 卡上约每卡
  28 GB，挂上未合并的 LoRA 后约每卡 36–38 GB。这些模型完全不经过
  bitsandbytes；带宽受限的单卡部署可设 ``PRTHINKER_QUANT=fp8``
  选用 FP8 权重。
* 其他模型名默认使用 8-bit bitsandbytes 量化。
  ``bitsandbytes`` 需要 CUDA；Windows 环境请使用上游
  ``bitsandbytes-windows-webui`` wheel，或直接在 WSL2 内运行。较小的
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
