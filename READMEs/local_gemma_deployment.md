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
| RAG embedding | `google/embeddinggemma-300m` (cosine threshold **0.32**) |

Rationale: one standardized local Gemma model keeps the shared HF cache,
Docker images, and LoRA adapters interchangeable across experiments on this
machine, and 31B bf16 (~65 GB) fits the GB10's 121 GB unified memory with
headroom for LoRA training.

## RAG embedding (EmbeddingGemma)

Local deployments default to `google/embeddinggemma-300m` for the FAISS
rule index (`codes/util/faiss_util.py`); `EMB_MODEL` overrides it, e.g.
`EMB_MODEL=Qwen/Qwen3-Embedding-4B` reproduces the legacy qwen-era index.

- EmbeddingGemma **is gated** on Hugging Face: accept the license on the
  model page once and set `HF_TOKEN`.
- It loads through **sentence-transformers** (`encode_query` /
  `encode_document`), never bare `AutoModel` — its embedding stack
  appends Dense projections and prompts after pooling, so mean-pooled
  hidden states live in a different vector space.
- The default cosine threshold is **0.32**, calibrated against the
  qwen-era retrieval sets (Qwen3-Embedding-4B @ 0.7) over the 44
  `code_to_detect` queries — see
  `codes/run/embedding_threshold_calibration.md`. EmbeddingGemma's
  scores run much lower (observed max 0.395 vs 0.761), so 0.7 retrieves
  nothing on the new model. `FaissRAGRetriever()` resolves the
  calibrated value automatically; pass an explicit `threshold=` to pin.
- The qwen inference server (`codes/run/fastapi_server.py`) and the qwen
  batch runner (`codes/run/cot.py`) pin `EMB_MODEL` to the legacy model
  so their behaviour is unchanged.

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
