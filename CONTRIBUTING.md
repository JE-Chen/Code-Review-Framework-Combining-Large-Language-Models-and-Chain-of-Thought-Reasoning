# Contributing

Use Python 3.12 or 3.13. Install the locked CI environment and project without
re-resolving dependencies:

```shell
python -m pip install --require-hashes -r requirements/ci.lock
python -m pip install -e . --no-deps
```

Before opening a pull request, run:

```shell
python -m pytest
ruff check prthinker tests
bandit -c pyproject.toml -r prthinker
python -m build
```

Tests that need a network service or GPU must use the registered `network`,
`integration`, or `gpu` marker and cannot run at import time. Update both `.in`
and generated `.lock` files when dependencies change. Do not commit downloaded
benchmark datasets, credentials, model weights, or fabricated evaluation
scores.
