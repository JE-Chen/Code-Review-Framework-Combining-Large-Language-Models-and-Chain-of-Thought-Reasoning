# Local Gemma Deployment Policy（本機 Gemma 部署規範）

> Scope: **this machine only** (the local DGX Spark / GB10 workstation).
> This policy does **not** restrict other users or other environments from
> deploying any other models (Qwen, Llama, other Gemma sizes, etc.).

## Policy

All **local** Gemma deployments — training, fine-tuning, and inference — use:

| Item | Value |
|---|---|
| Model | `google/gemma-4-31B-it` |
| Source | Hugging Face (not gated, no token required) |
| Precision | bf16 (no bitsandbytes — unreliable on aarch64/sm_121) |
| Min transformers | `>= 5.10` (first version with the `gemma4` architecture) |

Rationale: one standardized local Gemma model keeps the shared HF cache,
Docker images, and LoRA adapters interchangeable across experiments on this
machine, and 31B bf16 (~65 GB) fits the GB10's 121 GB unified memory with
headroom for LoRA training.

## Hardware notes (DGX Spark, GB10)

- Unified memory: GPU and CPU share 121 GB; `nvidia-smi` shows memory as
  `Not Supported` — use `~/.local/bin/gpumem` (cudaMemGetInfo) or `free -h`.
- GPU arch is sm_121 (Blackwell) on aarch64: use NGC PyTorch base images
  (`nvcr.io/nvidia/pytorch:25.09-py3` or newer), not pypi torch wheels.

## Training (LoRA fine-tune)

```bash
cd docker
docker compose -f docker-compose.train.yml up -d --build
docker logs -f gemma4-train      # console logs
# TensorBoard: http://localhost:6006
```

- Script: `codes/train/gemma4-31b.py`
- Data: `datas/fine_tuning_data/qwen3_train_data.jsonl`
  (JSONL, one object per line, keys: `Instruction`, `question`, `answer`,
  optional `think`)
- Output adapter: `codes/train/outputs-lora-gemma4-31b/`

Hyperparameters are env-overridable (`MODEL_NAME`, `NUM_EPOCHS`,
`MICRO_BATCH_SIZE`, `GA_STEPS`, `SEQ_LEN`, `LR`, `LORA_R`, ...) — overriding
`MODEL_NAME` is exactly how non-local or experimental runs deploy other
models; only the local default is fixed to `google/gemma-4-31B-it`.
