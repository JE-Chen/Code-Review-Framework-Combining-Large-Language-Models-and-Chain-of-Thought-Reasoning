# Locked environments

`runner.in` and `ci.in` are the human-edited inputs. Generate deterministic,
hash-checked lock files with:

```shell
uv pip compile --universal --generate-hashes --python-version 3.12 requirements/runner.in -o requirements/runner.lock
uv pip compile --universal --generate-hashes --python-version 3.12 requirements/ci.in -o requirements/ci.lock
```

`--universal` is required: it emits environment markers so one lock file
covers every platform. A lock compiled without it on one OS omits the other
platforms' conditional dependencies (e.g. `keyring`'s Linux-only
`secretstorage`) and `pip install --require-hashes` then fails on CI's
ubuntu runners.

CI and release changes that alter dependencies must regenerate both lock files.
The GPU server remains image-locked because PyTorch/CUDA wheels are platform
specific; its Dockerfile and image digest are the reproducibility boundary.
