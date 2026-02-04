import datetime

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

# 路徑：基底模型 + 你訓練好的 LoRA 輸出資料夾
base_model = "Qwen/Qwen3-30B-A3B-Thinking-2507"
lora_path = "./outputs-lora-qwen3-30b"

# 載入 tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,  # bf16 compute if supported
)

model = AutoModelForCausalLM.from_pretrained(
    base_model,
    device_map="auto",
    quantization_config=bnb_config,
)

# 套用 LoRA 權重
model = PeftModel.from_pretrained(model, lora_path)

print(datetime.datetime.now(), "Model loaded")

# 測試推論
prompt = """ 
Why is inconsistent or insufficient logging a risk in a production system?
"""
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
    max_new_tokens=16784
)

output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

try:
    index = len(output_ids) - output_ids[::-1].index(151668)
except ValueError:
    index = 0

thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
print(datetime.datetime.now(), "Generate done")

print(thinking_content)
print(content)
