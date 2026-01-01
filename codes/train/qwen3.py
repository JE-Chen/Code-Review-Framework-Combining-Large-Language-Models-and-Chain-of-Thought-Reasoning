import datetime
import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments, BitsAndBytesConfig,
)

MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen3-30B-A3B-Thinking-2507")
DATA_PATH = os.environ.get("DATA_PATH", "qwen3_train_data.jsonl")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "./outputs-lora-qwen-3-30b-a3b")

SEQ_LEN = int(os.environ.get("SEQ_LEN", 768))
MICRO_BATCH_SIZE = int(os.environ.get("MICRO_BATCH_SIZE", 1))
GRADIENT_ACCUMULATION_STEPS = int(os.environ.get("GA_STEPS", 64))
NUM_EPOCHS = float(os.environ.get("NUM_EPOCHS", 3))
LEARNING_RATE = float(os.environ.get("LR", 2e-4))
WARMUP_RATIO = float(os.environ.get("WARMUP_RATIO", 0.03))
WEIGHT_DECAY = float(os.environ.get("WEIGHT_DECAY", 0.0))

LORA_R = int(os.environ.get("LORA_R", 64))
LORA_ALPHA = int(os.environ.get("LORA_ALPHA", 128))
LORA_DROPOUT = float(os.environ.get("LORA_DROPOUT", 0.05))
TARGET_MODULES = os.environ.get(
    "TARGET_MODULES",
    "q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj"
).split(",")

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,  # bf16 compute if supported
)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    use_fast=True,
    trust_remote_code=True,
)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

dataset = load_dataset("json", data_files={"train": DATA_PATH}, split="train")

def ensure_io(example):
    if "Instruction" not in example or "answer" not in example:
        raise ValueError("每行 json 需要包含 'Instruction' 與 'answer'")
    return example

dataset = dataset.map(ensure_io)

def format_prompt(instruction: str, question: str, think: str, answer: str) -> str:
    return (
        f"任務：{instruction.strip()}\n"
        f"問題：{question.strip()}\n"
        f"思考：{think.strip()}\n"
        f"答案：{answer.strip()}"
    )

def tokenize_batch(batch):
    texts = [
        format_prompt(ins, q, t, ans)
        for ins, q, t, ans in zip(batch["Instruction"], batch["question"], batch["think"], batch["answer"])
    ]
    return tokenizer(
        texts,
        truncation=True,
        max_length=SEQ_LEN,
        padding=False,  # dynamic padding via collator
    )

tokenized = dataset.map(
    tokenize_batch,
    batched=True,
    remove_columns=dataset.column_names,
)

use_bf16 = torch.cuda.is_available() and torch.cuda.get_device_capability(0)[0] >= 8

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    trust_remote_code=True,
    quantization_config=bnb_config,  # quantization belongs here
)


# Prepare for k-bit training (important for stability & memory)
model = prepare_model_for_kbit_training(model)

peft_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=TARGET_MODULES,
)
print(datetime.datetime.now(), "Model loaded")
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

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
    bf16=use_bf16,  # compute in bf16 if available
    fp16=not use_bf16,
    optim="adamw_8bit",  # cut optimizer memory
    gradient_checkpointing=True,
    dataloader_pin_memory=True,
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
    print(datetime.datetime.now(), "Training complete")
    if merge_flag:
        print("Merging LoRA weights into base model...")
        merged_model = model.merge_and_unload()
        merged_model.save_pretrained(os.path.join(OUTPUT_DIR, "merged"))
        print("Merged model saved to:", os.path.join(OUTPUT_DIR, "merged"))

if __name__ == "__main__":
    main(merge_flag=False)