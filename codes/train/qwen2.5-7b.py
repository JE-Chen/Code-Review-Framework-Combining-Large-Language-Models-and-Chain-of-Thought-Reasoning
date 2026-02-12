import os
from pathlib import Path
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model

# ==============================
# 全域參數設定
# ==============================
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-Coder-7B-Instruct")
DATA_PATH = os.environ.get("DATA_PATH", str(Path("../../datas/fine_tuning_data/qwen3_train_data.jsonl")))
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "./outputs-lora-qwen2.5-coder-7b")

BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 2))
GRAD_ACCUM = int(os.environ.get("GRAD_ACCUM", 4))
EPOCHS = int(os.environ.get("EPOCHS", 3))
LEARNING_RATE = float(os.environ.get("LEARNING_RATE", 2e-5))
MAX_LENGTH = int(os.environ.get("MAX_LENGTH", 1024))

# ==============================
# 載入模型與 tokenizer
# ==============================
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    dtype=torch.bfloat16,
    device_map="auto"
)

# ==============================
# 載入資料集 (JSONL 格式)
# ==============================
def format_example(example):
    prompt = f"Instruction: {example['Instruction']}\nQuestion: {example['question']}\nThink: {example.get('think', '')}\nAnswer:"
    answer = example['answer']
    return {"prompt": prompt, "answer": answer}

dataset = load_dataset("json", data_files=DATA_PATH, split="train")
dataset = dataset.map(format_example)

def tokenize(batch):
    tokenized_prompt = tokenizer(
        batch["prompt"],
        truncation=True,
        max_length=MAX_LENGTH,
        padding=False,
        add_special_tokens=False,
    )
    tokenized_answer = tokenizer(
        batch["answer"],
        truncation=True,
        max_length=MAX_LENGTH,
        padding=False,
        add_special_tokens=False,
    )

    input_ids = []
    labels = []
    for p_ids, a_ids in zip(tokenized_prompt["input_ids"], tokenized_answer["input_ids"]):
        input_id = p_ids + a_ids + [tokenizer.eos_token_id]
        input_ids.append(input_id)

        label = [-100] * len(p_ids) + a_ids + [tokenizer.eos_token_id]
        labels.append(label)

    max_len = max(len(ids) for ids in input_ids)
    for i in range(len(input_ids)):
        pad_len = max_len - len(input_ids[i])
        input_ids[i] = input_ids[i] + [tokenizer.pad_token_id] * pad_len
        labels[i] = labels[i] + [-100] * pad_len

    return {
        "input_ids": input_ids,
        "attention_mask": [[1]*len(ids) + [0]*pad_len for ids, pad_len in zip(input_ids, [max_len - len(ids) for ids in input_ids])],
        "labels": labels,
    }

tokenized_dataset = dataset.map(tokenize, batched=True, remove_columns=["prompt", "answer"])

# ==============================
# LoRA 設定
# ==============================
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# ==============================
# 🏋️ 訓練參數
# ==============================
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM,
    num_train_epochs=EPOCHS,
    learning_rate=LEARNING_RATE,
    fp16=True,
    logging_steps=10,
    save_steps=100,
    save_total_limit=2,
)

# ==============================
# 🚀 Trainer
# ==============================
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer
)

# ==============================
# 開始訓練
# ==============================
trainer.train()

# ==============================
# 儲存 LoRA 權重
# ==============================
model.save_pretrained(OUTPUT_DIR)
