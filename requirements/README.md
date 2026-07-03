# Locked environments

`runner.in` and `ci.in` are the human-edited inputs. Generate deterministic,
hash-checked lock files with:

```shell
python -m pip install pip-tools
pip-compile --generate-hashes --strip-extras -o requirements/runner.lock requirements/runner.in
pip-compile --generate-hashes --strip-extras -o requirements/ci.lock requirements/ci.in
```

CI and release changes that alter dependencies must regenerate both lock files.
The GPU server remains image-locked because PyTorch/CUDA wheels are platform
specific; its Dockerfile and image digest are the reproducibility boundary.
