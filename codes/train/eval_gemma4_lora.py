"""Before/after sanity check for the gemma-4-31B code-review LoRA.

Loads the base model once, attaches the adapter, and answers a few
code-review questions twice — with the adapter disabled (baseline) and
enabled (fine-tuned) — writing a side-by-side markdown report.

Run inside the training image (see docker/docker-compose.train.yml):
    docker compose -f docker-compose.train.yml run --rm gemma4-train \
        python codes/train/eval_gemma4_lora.py
"""

import datetime
import os

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch
from peft import PeftModel
from transformers import AutoTokenizer

MODEL_NAME = os.environ.get("MODEL_NAME", "google/gemma-4-31B-it")
ADAPTER_DIR = os.environ.get(
    "ADAPTER_DIR", "/workspace/codes/train/outputs-lora-gemma4-31b"
)
REPORT_PATH = os.environ.get(
    "REPORT_PATH", "/workspace/codes/train/eval-results-gemma4-31b.md"
)
MAX_NEW_TOKENS = int(os.environ.get("MAX_NEW_TOKENS", 400))

# Two questions in the style of the training corpus plus one novel,
# code-specific question the corpus never asked (generalization probe).
QUESTIONS = [
    (
        "Perform an in-depth code review.",
        "Business rules related to pricing and discounts are duplicated "
        "across checkout, billing, and reporting modules. Why is this "
        "dangerous at scale?",
    ),
    (
        "Review time handling.",
        "System time is accessed directly throughout the code. Why does "
        "this complicate testing?",
    ),
    (
        "Perform an in-depth code review.",
        "A Python service opens a new database connection inside a request "
        "handler and never closes it on the exception path:\n\n"
        "def get_user(user_id):\n"
        "    conn = psycopg2.connect(DSN)\n"
        "    row = conn.cursor().execute(\n"
        "        'SELECT * FROM users WHERE id = %s', (user_id,)\n"
        "    ).fetchone()\n"
        "    conn.close()\n"
        "    return row\n\n"
        "What problems do you see and how would you fix them?",
    ),
]

# Mirror the training prompt exactly (first PROMPT_TEMPLATES entry).
PROMPT_TEMPLATE = "Task: {instruction}\nQuestion: {question}\nAnswer:"


def build_inputs(tokenizer, instruction, question):
    prompt = PROMPT_TEMPLATE.format(
        instruction=instruction.strip(), question=question.strip()
    )
    # Training prepended <bos> manually with add_special_tokens=False.
    ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    if tokenizer.bos_token_id is not None:
        ids = [tokenizer.bos_token_id] + ids
    return torch.tensor([ids])


def generate(model, tokenizer, input_ids):
    input_ids = input_ids.to(model.device)
    with torch.no_grad():
        out = model.generate(
            input_ids=input_ids,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            temperature=None,
            top_p=None,
            top_k=None,
            pad_token_id=tokenizer.pad_token_id,
        )
    return tokenizer.decode(
        out[0][input_ids.shape[1]:], skip_special_tokens=True
    ).strip()


def load_model():
    from transformers import AutoModelForImageTextToText

    print(datetime.datetime.now(), "Loading base model...", flush=True)
    model = AutoModelForImageTextToText.from_pretrained(
        MODEL_NAME,
        dtype=torch.bfloat16,
        trust_remote_code=True,
        attn_implementation=os.environ.get("ATTN_IMPL", "sdpa"),
        device_map="auto",
    )
    print(datetime.datetime.now(), "Attaching adapter...", flush=True)
    model = PeftModel.from_pretrained(model, ADAPTER_DIR)
    model.eval()
    return model


def main():
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME, trust_remote_code=True, use_fast=True
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = load_model()

    sections = []
    for i, (instruction, question) in enumerate(QUESTIONS, 1):
        input_ids = build_inputs(tokenizer, instruction, question)

        print(datetime.datetime.now(), f"Q{i}: baseline generate", flush=True)
        with model.disable_adapter():
            base_answer = generate(model, tokenizer, input_ids)

        print(datetime.datetime.now(), f"Q{i}: adapter generate", flush=True)
        lora_answer = generate(model, tokenizer, input_ids)

        sections.append(
            f"## Q{i}: {instruction}\n\n"
            f"**Question:** {question}\n\n"
            f"### Base model (adapter disabled)\n\n{base_answer}\n\n"
            f"### Fine-tuned (adapter enabled)\n\n{lora_answer}\n"
        )
        print(datetime.datetime.now(), f"Q{i} done", flush=True)

    header = (
        f"# gemma-4-31B-it LoRA before/after — "
        f"{datetime.datetime.now():%Y-%m-%d %H:%M}\n\n"
        f"Adapter: `{ADAPTER_DIR}` · greedy decoding · "
        f"max_new_tokens={MAX_NEW_TOKENS}\n\n"
    )
    with open(REPORT_PATH, "w") as f:
        f.write(header + "\n".join(sections))
    print(datetime.datetime.now(), f"Report written to {REPORT_PATH}", flush=True)


if __name__ == "__main__":
    main()
