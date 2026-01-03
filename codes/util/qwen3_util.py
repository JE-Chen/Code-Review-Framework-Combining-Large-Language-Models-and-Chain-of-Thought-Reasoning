import datetime

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import os

from codes.util.memory import get_max_memory

def load_qwen3_model():

    os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"

    model_name = "Qwen/Qwen3-30B-A3B-Thinking-2507"

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,  # bf16 compute if supported
    )

    # === 一次載入模型與 tokenizer ===
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    print("Loading model across all GPUs...")
    max_memory = get_max_memory()
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        max_memory=max_memory if max_memory else None,
        quantization_config=bnb_config,
    )
    print(datetime.datetime.now(), "Model loaded")
    return model, tokenizer

def qwen3_ask(system_prompt: str, prompt: str, model, tokenizer, max_new_tokens: int = 16784):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=max_new_tokens
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

    try:
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
    print(datetime.datetime.now(), "Generate done")
    return content, thinking_content

