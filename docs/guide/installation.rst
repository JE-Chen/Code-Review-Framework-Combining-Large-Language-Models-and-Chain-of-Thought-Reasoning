Installation
============

``reviewmind`` ships as a Python package with three install profiles.
Pick the one that matches where the code will run.

Profiles
--------

============= =========================================================
Profile       What it installs
============= =========================================================
*(base)*      ``httpx``, ``pydantic`` — enough to call a remote inference
              server and post to GitHub. **Use this on CI runners** so the
              job stays small and fast.
``runner``    Alias of base (kept for clarity in workflows).
``local``     ``transformers``, ``torch``, ``accelerate``, ``bitsandbytes``,
              ``peft``, ``faiss-cpu``, ``numpy``. Use this when running the
              full pipeline in-process — typically on a GPU dev box.
``server``    ``fastapi``, ``uvicorn`` (on top of ``local``). Use this on
              the machine that hosts the inference server.
============= =========================================================

Install
-------

From a checkout of the repo:

.. code-block:: bash

   # CI runner / thin client
   pip install -e ".[runner]"

   # Local dev (in-process inference)
   pip install -e ".[local]"

   # Server (hosts /ask, /rag, /review)
   pip install -e ".[server]"

Python version
--------------

Python ``>=3.12`` is required — the package uses PEP 604 union syntax
(``str | None``) and ``dataclass(slots=True, kw_only=True)`` patterns.

GPU notes
---------

* ``bitsandbytes`` requires CUDA. On Windows, use the upstream
  ``bitsandbytes-windows-webui`` wheel or run inside WSL2.
* The Qwen3-Coder-30B model loads with 4-bit NF4 quantization
  (≈ 18 GB VRAM). Smaller LoRA targets (Qwen3-1.7B, Qwen2.5-Coder-7B)
  fit on a single 12 GB card.

Embedding model
---------------

The RAG retriever uses ``Qwen/Qwen3-Embedding-4B`` (~ 8 GB VRAM). On CI
runners you should leave the embedding model off and use the remote ``/rag``
endpoint instead — see :doc:`/concepts/rag-and-rules`.

Verifying the install
---------------------

.. code-block:: bash

   # The CLI should respond with subcommand help
   reviewmind --help

   # The five built-in CoT steps should be registered
   python -c "from reviewmind.steps import registered_steps; \
              print([s.name for s in registered_steps()])"

Expected output::

   ['first_summary', 'first_code_review', 'linter', 'code_smell', 'total_summary']
