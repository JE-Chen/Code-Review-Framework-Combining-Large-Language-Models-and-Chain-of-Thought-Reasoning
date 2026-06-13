"""QLoRA fine-tune for google/gemma-4-31B-it (dense, 30.7B, 256K context).

Adapted from qwen3-coder-30b.py. Differences that matter:

* ``google/gemma-4-31B-it-assistant`` is NOT this model — its config is a
  4-layer / hidden-1024 MTP draft model used only to speculatively decode
  the 31B target. Fine-tuning the draft alone does nothing for review
  quality, so this script defaults to the target ``google/gemma-4-31B-it``
  (override with MODEL_NAME if you really mean the draft).
* The ``gemma4`` model_type requires transformers>=5.7 (the Hub config is
  emitted by 5.7.0.dev0). Train in a venv/image SEPARATE from the
  inference server, whose Qwen3-A3B deploy pins transformers<5. Gemma 4
  is dense, so the Qwen3-MoE densification OOM behind that pin does not
  apply to this training run.
* Prompts go through ``tokenizer.apply_chat_template`` so the trained
  turn format matches what the serve path produces — Gemma -it
  checkpoints are strict about their turn markers, and plain-text
  prompts degrade them.
* TARGET_MODULES defaults to ``all-linear``: Gemma 4's hybrid attention
  (unified K/V on global layers) does not keep one projection-name set
  across layers, so a fixed suffix list can miss layers. Override with a
  comma-separated list to pin specific modules.
"""

import datetime
import os
import random
from pathlib import Path

# TOKENIZERS_PARALLELISM must be set before transformers/tokenizers import.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# pylint: disable=wrong-import-position  # env var above must precede heavy imports
import torch  # noqa: E402
from datasets import load_dataset  # noqa: E402
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training  # noqa: E402
from transformers import (  # noqa: E402
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
MODEL_NAME = os.environ.get("MODEL_NAME", "google/gemma-4-31B-it")
DATA_PATH = os.environ.get("DATA_PATH", str(Path("../../datas/fine_tuning_data/qwen3_train_data.jsonl")))
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "./outputs-qlora-gemma-4-31b-it")

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

# "all-linear" is a PEFT keyword (every nn.Linear except the LM head); a
# comma list (e.g. "q_proj,o_proj") targets specific suffixes instead.
_RAW_TARGET_MODULES = os.environ.get("TARGET_MODULES", "all-linear")
TARGET_MODULES = (
    _RAW_TARGET_MODULES
    if _RAW_TARGET_MODULES == "all-linear"
    else _RAW_TARGET_MODULES.split(",")
)

# ======================
# Tokenizer
# ======================
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
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

def build_user_content(instruction, question, think):  # pylint: disable=unused-argument  # think kept to match dataset field
    template = random.choice(PROMPT_TEMPLATES)  # nosec B311  # non-crypto: training-data shuffle, not security-sensitive
    return template.format(
        instruction=instruction.strip(),
        question=question.strip(),
    )


# Plain-text marker the template passes through verbatim; it only exists
# to locate where assistant content lands in the rendered conversation.
_PROBE_SENTINEL = "PRTHINKERPROBE7339"


def _derive_turn_close() -> str:
    """Return the literal the chat template appends after assistant content.

    Gemma 4's generation prompt is NOT a prefix of its full-conversation
    render: ``add_generation_prompt=True`` appends an empty thought
    channel (``<|channel>thought ... <channel|>``) that the assistant-turn
    render omits, so rendering the answered conversation would both break
    the label mask and train a context the serve path never produces.
    Training text is instead built as generation prompt + answer + turn
    close; this derives the turn-close suffix from a sentinel render
    rather than hardcoding the marker.
    """
    probe = tokenizer.apply_chat_template(
        [
            {"role": "user", "content": "probe"},
            {"role": "assistant", "content": _PROBE_SENTINEL},
        ],
        tokenize=False,
        add_generation_prompt=False,
    )
    _head, sep, tail = probe.partition(_PROBE_SENTINEL)
    if not sep:
        raise ValueError(
            "chat template transformed the probe sentinel; cannot derive "
            "the turn-close suffix for label masking"
        )
    return tail


_TURN_CLOSE = _derive_turn_close()


def build_chat_strings(user_content, answer):
    """Build the masked prompt and the full training text for one row.

    The prompt is the exact ``add_generation_prompt=True`` render the
    serve path puts in front of the model (including Gemma 4's empty
    thought channel), so the string-prefix property the label mask needs
    holds by construction. ``_require_prompt_prefix`` still validates the
    token-level form on every row.
    """
    messages = [{"role": "user", "content": user_content}]
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    return prompt, prompt + answer.strip() + _TURN_CLOSE

# ======================
# Tokenization with label masking
# ======================
def _require_prompt_prefix(prompt_ids: list, full_ids: list) -> None:
    """Raise if the prompt tokens are not a prefix of the full-text tokens.

    The label mask blanks the first ``len(prompt_ids)`` positions, so a
    violation would silently train on prompt tokens (tokenizer merged
    across the model-turn boundary) or emit labels longer than the
    truncated input (prompt alone exceeds SEQ_LEN). Fail loudly instead.
    """
    if full_ids[: len(prompt_ids)] == prompt_ids:
        return
    mismatch = next(
        (i for i, (p, f) in enumerate(zip(prompt_ids, full_ids)) if p != f),
        min(len(prompt_ids), len(full_ids)),
    )
    raise ValueError(
        "prompt is not a token-level prefix of the full chat rendering: "
        f"first mismatch at token {mismatch} "
        f"(prompt_len={len(prompt_ids)}, full_len={len(full_ids)}); "
        "label masking would be misaligned"
    )


def tokenize_batch(batch):
    input_ids = []
    labels = []

    for ins, q, t, ans in zip(
        batch["Instruction"],
        batch["question"],
        batch["think"],
        batch["answer"],
    ):
        user_content = build_user_content(ins, q, t)
        prompt, full_text = build_chat_strings(user_content, ans)

        # The chat template already emits BOS/turn markers.
        tok_prompt = tokenizer(prompt, add_special_tokens=False)
        tok_full = tokenizer(
            full_text,
            truncation=True,
            max_length=SEQ_LEN,
            add_special_tokens=False,
        )

        prompt_len = len(tok_prompt["input_ids"])
        full_ids = tok_full["input_ids"]
        _require_prompt_prefix(tok_prompt["input_ids"], full_ids)

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
