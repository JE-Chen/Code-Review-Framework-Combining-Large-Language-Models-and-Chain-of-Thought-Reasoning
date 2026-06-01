# FAISS install on the remote GPU server (conda)

These commands are **not** pip-format and **not** consumed by any of the
project's pyproject.toml extras. They live here only to document how to
provision FAISS on the GPU host that runs `codes/run/fastapi_server.py`,
where the bundled `pip install -e ".[server]"` cannot pull a CUDA-aware
FAISS build directly.

> Why a separate file: Dependabot's pip ecosystem scanner used to choke on
> the prior `conda_requirements.txt` filename — it would try to parse
> `conda install …` lines as pip requirement specifiers and fail the
> update job. Keeping the conda notes in a Markdown file (and not under a
> `*requirements*.txt` name) avoids that auto-detection.

## On the GPU host

### Option A — GPU build (CUDA-aware FAISS)

```bash
conda install conda-forge::mkl==2024.2.2
conda install -c pytorch -c nvidia faiss-gpu=1.13.2
```

### Option B — CPU-only build

Use this on a host without an NVIDIA GPU, or when memory-mapped FAISS
indexes are good enough for the workload.

```bash
conda install conda-forge::faiss-cpu
```

Pick exactly one of (A) and (B); installing both is unsupported.

## What this is *not*

- A pip requirements file. The pyproject.toml `[runner]` / `[local]` /
  `[server]` extras own the pip side; nothing here should ever be passed
  to `pip install -r`.
- Required for the runner profile (`pip install -e ".[runner]"`). The
  runner talks to the FastAPI server over httpx and never imports FAISS.
- A part of the runner's CI matrix. GitHub Actions runs the runner extra
  only; FAISS lives on the GPU host.
