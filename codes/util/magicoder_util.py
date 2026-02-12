import datetime
import os
import re

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from codes.util.memory import get_max_memory


def load_magicoder_model():
    os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"
    # === 模型與 tokenizer 只載一次 ===
    model_id = "ise-uiuc/Magicoder-S-DS-6.7B"
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    print("Loading model across all GPUs...")
    max_memory = get_max_memory()
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        max_memory=max_memory if max_memory else None,
        torch_dtype=torch.bfloat16,
        low_cpu_mem_usage=True
    )

    # Tokenize 並送到第一個分片所在的裝置
    first_dev = next(iter(model.hf_device_map.values()))
    if isinstance(first_dev, int):
        device = torch.device(f"cuda:{first_dev}")
    elif isinstance(first_dev, str) and first_dev.startswith("cuda"):
        device = torch.device(first_dev)
    else:
        device = torch.device("cpu")
    print(datetime.datetime.now(), "Model loaded")
    return model, tokenizer, device


def magicoder_ask(prompt: str, model, tokenizer, device):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )

    result_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    match = re.search(r"@@ Response\s*(.*)", result_text, re.DOTALL)
    if match:
        result_text = match.group(1).strip()
    print(datetime.datetime.now(), "Generation completed.")
    return result_text
