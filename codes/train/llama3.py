import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)


MODEL_NAME = os.environ.get("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
DATA_PATH = os.environ.get("DATA_PATH", "data.jsonl")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "./outputs-qlora-llama3-8b")

SEQ_LEN = int(os.environ.get("SEQ_LEN", 1024))
MICRO_BATCH_SIZE = int(os.environ.get("MICRO_BATCH_SIZE", 1))
GRADIENT_ACCUMULATION_STEPS = int(os.environ.get("GA_STEPS", 16))
NUM_EPOCHS = float(os.environ.get("NUM_EPOCHS", 100))
LEARNING_RATE = float(os.environ.get("LR", 2e-4))
WARMUP_RATIO = float(os.environ.get("WARMUP_RATIO", 0.03))
WEIGHT_DECAY = float(os.environ.get("WEIGHT_DECAY", 0.0))

LORA_R = int(os.environ.get("LORA_R", 64))
LORA_ALPHA = int(os.environ.get("LORA_ALPHA", 16))
LORA_DROPOUT = float(os.environ.get("LORA_DROPOUT", 0.05))
TARGET_MODULES = os.environ.get(
    "TARGET_MODULES",
    "q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj"
).split(",")


bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)


tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    use_fast=True,
    trust_remote_code=True,
)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"


dataset = load_dataset(
    "json",
    data_files={"train": DATA_PATH},
    split="train",
)

def ensure_io(example):
    """檢查 instruction/output 欄位"""
    if "instruction" not in example or "output" not in example:
        raise ValueError("每行 json 需要包含 'instruction' 與 'output'")
    return example

dataset = dataset.map(ensure_io)

def format_prompt(instruction: str, output: str) -> str:
    """
    最簡單的格式：直接把問題和答案接在一起
    """
    return f"問題：{instruction.strip()}\n答案：{output.strip()}"

def tokenize_batch(batch):
    texts = [format_prompt(ins, out) for ins, out in zip(batch["instruction"], batch["output"])]
    return tokenizer(
        texts,
        truncation=True,
        max_length=SEQ_LEN,
        padding="max_length",  # 或 "longest"，視需求
    )

tokenized = dataset.map(
    tokenize_batch,
    batched=True,
    remove_columns=dataset.column_names,
)


model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)
model = prepare_model_for_kbit_training(model)

peft_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=TARGET_MODULES,
)
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

use_bf16 = torch.cuda.is_available() and torch.cuda.get_device_capability(0)[0] >= 8

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=MICRO_BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
    num_train_epochs=NUM_EPOCHS,
    learning_rate=LEARNING_RATE,
    weight_decay=WEIGHT_DECAY,
    warmup_ratio=WARMUP_RATIO,
    lr_scheduler_type="cosine",
    logging_steps=10,
    save_steps=200,
    save_total_limit=3,
    bf16=use_bf16,
    fp16=not use_bf16,
    optim="paged_adamw_32bit",
    gradient_checkpointing=True,
    dataloader_pin_memory=True,
    dataloader_num_workers=2,
    max_grad_norm=1.0,
    torch_compile=False,
    report_to=[],
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized,
    processing_class=tokenizer,
    data_collator=data_collator,
)

def main(merge_flag: bool = False):
    trainer.train()
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    if merge_flag:
        print("Merging LoRA weights into base model...")
        merged_model = model.merge_and_unload()
        merged_model.save_pretrained(os.path.join(OUTPUT_DIR, "merged"))
        print("Merged model saved to:", os.path.join(OUTPUT_DIR, "merged"))

if __name__ == "__main__":
    main(merge_flag=False)