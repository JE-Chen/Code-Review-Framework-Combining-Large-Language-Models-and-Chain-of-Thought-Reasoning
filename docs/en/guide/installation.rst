Installation
============

``prthinker`` ships as a Python package with three install profiles.
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

Locked environments
-------------------

For a bit-for-bit reproducible install (what CI runs on every PR), use
the hash-locked requirement files under ``requirements/`` instead of
letting pip re-resolve dependencies:

.. code-block:: bash

   # Runner profile, exact pinned wheels verified by hash
   pip install --require-hashes -r requirements/runner.lock
   pip install -e . --no-deps

   # Full CI toolchain (pytest, ruff, bandit, build, twine)
   pip install --require-hashes -r requirements/ci.lock
   pip install -e . --no-deps

``runner.in`` / ``ci.in`` are the human-edited inputs; regenerate the
locks with ``pip-compile --generate-hashes`` when dependencies change
(see ``requirements/README.md``). The GPU server stays image-locked
instead — PyTorch/CUDA wheels are platform-specific, so its Dockerfile
and image digest are the reproducibility boundary.

Python version
--------------

Python ``>=3.12`` is required — the package uses PEP 604 union syntax
(``str | None``) and ``dataclass(slots=True, kw_only=True)`` patterns.

GPU notes
---------

* The bf16-family models (``Qwen3-Coder-30B-A3B``, ``Qwen3-30B-A3B``,
  ``gemma-4-31B-it``) load in plain **bf16** with a balanced
  ``device_map="auto"`` split — ≈ 28 GB per card for the 30B MoE base
  across two 46 GB cards, ~36–38 GB per card once the unmerged LoRA is
  attached. No bitsandbytes is involved for these models; set
  ``PRTHINKER_QUANT=fp8`` to opt into FP8 weights on
  bandwidth-bound single-card deploys.
* Other model names default to 8-bit bitsandbytes quantization.
  ``bitsandbytes`` requires CUDA; on Windows, use the upstream
  ``bitsandbytes-windows-webui`` wheel or run inside WSL2. Smaller LoRA
  targets (Qwen3-1.7B, Qwen2.5-Coder-7B) fit on a single 12 GB card.

Embedding model
---------------

The local RAG retriever defaults to ``google/embeddinggemma-300m`` (a
gated Hugging Face repo — accept the license once and set ``HF_TOKEN``),
loaded through sentence-transformers, with a calibrated cosine threshold
of 0.32. Set ``EMB_MODEL=Qwen/Qwen3-Embedding-4B`` (~ 8 GB VRAM,
threshold 0.7) to reproduce the legacy index; the bundled inference
server pins this legacy model itself. On CI runners you should leave the
embedding model off and use the remote ``/rag`` endpoint instead — see
:doc:`../concepts/rag-and-rules`.

Verifying the install
---------------------

.. code-block:: bash

   # The CLI should respond with subcommand help
   prthinker --help

   # The five built-in CoT steps should be registered
   python -c "from prthinker.steps import registered_steps; \
              print([s.name for s in registered_steps()])"

Expected output::

   ['first_summary', 'first_code_review', 'linter', 'code_smell', 'total_summary']
