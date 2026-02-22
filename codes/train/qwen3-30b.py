import datetime
import os
import random
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from pathlib import Path
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    BitsAndBytesConfig,
    default_data_collator,
)

# ======================
# Config
# ======================
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen3-30B-A3B-Thinking-2507")
DATA_PATH = os.environ.get("DATA_PATH", str(Path("../../datas/fine_tuning_data/qwen3_train_data.jsonl")))
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "./outputs-lora-qwen3-30b")

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

TARGET_MODULES = os.environ.get(
    "TARGET_MODULES",
    "q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj"
).split(",")

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

        tok_prompt = tokenizer(prompt, add_special_tokens=False)
        tok_full = tokenizer(
            full_text,
            truncation=True,
            max_length=SEQ_LEN,
            add_special_tokens=False,
        )

        prompt_len = len(tok_prompt["input_ids"])
        full_ids = tok_full["input_ids"]

        # ⬇only answer tokens get loss
        label = [-100] * prompt_len + full_ids[prompt_len:]

        input_ids.append(full_ids)
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
data_collator = default_data_collator

# ======================
# Model (QLoRA)
# ======================
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    trust_remote_code=True,
    quantization_config=bnb_config,
)

model = prepare_model_for_kbit_training(model)

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
use_bf16 = torch.cuda.is_available() and torch.cuda.get_device_capability(0)[0] >= 8

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=MICRO_BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
    num_train_epochs=NUM_EPOCHS,
    learning_rate=LEARNING_RATE,
    warmup_ratio=WARMUP_RATIO,
    weight_decay=WEIGHT_DECAY,
    lr_scheduler_type="cosine",
    logging_steps=10,
    save_steps=200,
    save_total_limit=3,
    bf16=use_bf16,
    fp16=not use_bf16,
    optim="adamw_8bit",
    gradient_checkpointing=True,
    max_grad_norm=1.0,
    report_to=[],
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
