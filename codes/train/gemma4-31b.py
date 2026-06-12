import datetime
import math
import os
import random
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from pathlib import Path
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Trainer,
    TrainingArguments,
)

# ======================
# Config
# ======================
# Local deployment policy: all local Gemma runs use google/gemma-4-31B-it
# (see READMEs/local_gemma_deployment.md). The repo is NOT gated on HF.
# Requires transformers >= 5.10 (gemma4 architecture).
MODEL_NAME = os.environ.get("MODEL_NAME", "google/gemma-4-31B-it")
DATA_PATH = os.environ.get("DATA_PATH", str(Path("../../datas/fine_tuning_data/qwen3_train_data.jsonl")))
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "./outputs-lora-gemma4-31b")
LOGGING_DIR = os.environ.get("LOGGING_DIR", "./tb-logs/gemma4-31b")

SEQ_LEN = int(os.environ.get("SEQ_LEN", 1024))
MICRO_BATCH_SIZE = int(os.environ.get("MICRO_BATCH_SIZE", 1))
GRADIENT_ACCUMULATION_STEPS = int(os.environ.get("GA_STEPS", 64))

NUM_EPOCHS = float(os.environ.get("NUM_EPOCHS", 3))

LEARNING_RATE = float(os.environ.get("LR", 2e-5))

WARMUP_RATIO = float(os.environ.get("WARMUP_RATIO", 0.1))
WEIGHT_DECAY = float(os.environ.get("WEIGHT_DECAY", 0.01))

LORA_R = int(os.environ.get("LORA_R", 64))
LORA_ALPHA = int(os.environ.get("LORA_ALPHA", 64))

LORA_DROPOUT = float(os.environ.get("LORA_DROPOUT", 0.1))

# Restrict LoRA to the language model: gemma-4 vision-tower projections are
# Gemma4ClippableLinear, which PEFT cannot wrap (and we don't want to tune
# vision anyway). Default is a full-path regex; TARGET_MODULES env (comma
# list of suffixes) overrides it.
_tm_env = os.environ.get("TARGET_MODULES", "")
TARGET_MODULES = (
    _tm_env.split(",")
    if _tm_env
    else r".*language_model.*\.(q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj)$"
)

# ======================
# Tokenizer
# ======================
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    use_fast=True,
)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# ======================
# Dataset
# ======================
dataset = load_dataset("json", data_files={"train": DATA_PATH})["train"]

REQUIRED_KEYS = {"Instruction", "question", "answer"}

def check_keys(example):
    missing = REQUIRED_KEYS - example.keys()
    if missing:
        raise ValueError(f"Missing keys: {missing}")
    example.setdefault("think", "")
    return example

dataset = dataset.map(check_keys)

# ======================
# Prompt templates (ANTI OVERFIT)
# ======================
PROMPT_TEMPLATES = [
    "Task: {instruction}\nQuestion: {question}\nAnswer:",
    "You are a senior engineer.\n{instruction}\n\n{question}\n\nAnswer:",
    "Please carefully answer the following.\n{question}\n\nAnswer:",
]

def build_prompt(instruction, question, think):
    template = random.choice(PROMPT_TEMPLATES)
    return template.format(
        instruction=instruction.strip(),
        question=question.strip(),
    )

# ======================
# Tokenization with label masking
# ======================
# Unlike the Qwen scripts, Gemma needs <bos> at the start of every sequence;
# an <eos> is appended so the adapter learns to stop.
BOS = [tokenizer.bos_token_id] if tokenizer.bos_token_id is not None else []
EOS = [tokenizer.eos_token_id] if tokenizer.eos_token_id is not None else []

def tokenize_batch(batch):
    input_ids = []
    labels = []

    for ins, q, t, ans in zip(
        batch["Instruction"],
        batch["question"],
        batch["think"],
        batch["answer"],
    ):
        prompt = build_prompt(ins, q, t)
        full_text = prompt + " " + ans.strip()

        tok_prompt = tokenizer(prompt, add_special_tokens=False)["input_ids"]
        tok_full = tokenizer(
            full_text,
            truncation=True,
            max_length=SEQ_LEN - len(BOS) - len(EOS),
            add_special_tokens=False,
        )["input_ids"]

        prompt_len = min(len(tok_prompt), len(tok_full))

        # ⬇only answer tokens get loss
        ids = BOS + tok_full + EOS
        label = [-100] * (len(BOS) + prompt_len) + tok_full[prompt_len:] + EOS

        input_ids.append(ids)
        labels.append(label)

    return {"input_ids": input_ids, "labels": labels}

tokenized = dataset.shuffle(seed=42).map(
    tokenize_batch,
    batched=True,
    remove_columns=dataset.column_names,
)

# ======================
# Data collator (padding)
# ======================
data_collator = DataCollatorForSeq2Seq(
    tokenizer,
    padding=True,
    label_pad_token_id=-100,
)

# ======================
# Model (bf16 LoRA — no bitsandbytes: GB10 unified memory fits 31B in bf16
# (~65 GB), and bnb CUDA kernels are unreliable on aarch64/sm_121)
# ======================
def load_base_model():
    kwargs = dict(
        dtype=torch.bfloat16,
        trust_remote_code=True,
        # flash_attention_2 cannot be used: gemma-4-31B's head_dim exceeds
        # flash-attn's 256 limit. sdpa is the fastest remaining option; if
        # loss goes NaN, set ATTN_IMPL=eager.
        attn_implementation=os.environ.get("ATTN_IMPL", "sdpa"),
    )
    try:
        return AutoModelForCausalLM.from_pretrained(MODEL_NAME, **kwargs)
    except ValueError:
        # gemma-4 checkpoints are multimodal (Gemma4ForConditionalGeneration)
        from transformers import AutoModelForImageTextToText
        return AutoModelForImageTextToText.from_pretrained(MODEL_NAME, **kwargs)

model = load_base_model()
model.config.use_cache = False
model.enable_input_require_grads()

peft_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    target_modules=TARGET_MODULES,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, peft_config)
model.print_trainable_parameters()

# ======================
# Training
# ======================
# transformers v5 deprecations: warmup_ratio -> explicit warmup_steps,
# logging_dir -> TENSORBOARD_LOGGING_DIR env var.
steps_per_epoch = math.ceil(len(tokenized) / (MICRO_BATCH_SIZE * GRADIENT_ACCUMULATION_STEPS))
total_steps = round(steps_per_epoch * NUM_EPOCHS)
warmup_steps = max(1, int(WARMUP_RATIO * total_steps))
os.environ["TENSORBOARD_LOGGING_DIR"] = LOGGING_DIR

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=MICRO_BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
    num_train_epochs=NUM_EPOCHS,
    learning_rate=LEARNING_RATE,
    warmup_steps=warmup_steps,
    weight_decay=WEIGHT_DECAY,
    lr_scheduler_type="cosine",
    logging_steps=1,
    save_steps=20,
    save_total_limit=3,
    bf16=True,
    optim="adamw_torch_fused",
    gradient_checkpointing=True,
    gradient_checkpointing_kwargs={"use_reentrant": False},
    max_grad_norm=1.0,
    report_to=["tensorboard"],
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized,
    processing_class=tokenizer,
    data_collator=data_collator,
)

# ======================
# Main
# ======================
def main(merge_lora: bool = False):
    print(datetime.datetime.now(), "Start training")
    trainer.train()

    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    if merge_lora:
        print("Merging LoRA into base model...")
        merged = model.merge_and_unload()
        merged.save_pretrained(os.path.join(OUTPUT_DIR, "merged"))

    print(datetime.datetime.now(), "Training finished")

if __name__ == "__main__":
    main(merge_lora=False)
