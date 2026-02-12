import datetime

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel


def load_qwen3_model(lora_path: str = None, model_name: str = "Qwen/Qwen3-30B-A3B-Thinking-2507"):

    print("Loading model across all GPUs...")
    if model_name in ["Qwen/Qwen3-30B-A3B-Thinking-2507"]:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,  # bf16 compute if supported
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            quantization_config=bnb_config,
        )
    else:
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            quantization_config=bnb_config,
        )

    print(datetime.datetime.now(), "Model loaded")

    # === 一次載入模型與 tokenizer ===
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if lora_path:
        model = PeftModel.from_pretrained(model, lora_path)
        print(datetime.datetime.now(), "LoRa loaded")

    return model, tokenizer

def qwen3_ask(prompt: str, model, tokenizer, max_new_tokens: int = 16784):
    messages = [
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
    print(datetime.datetime.now(), "Generation completed.")
    return content, thinking_content

