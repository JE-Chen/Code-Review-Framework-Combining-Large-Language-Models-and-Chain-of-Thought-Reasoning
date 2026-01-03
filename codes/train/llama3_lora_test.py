import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# 路徑：基底模型 + 你訓練好的 LoRA 輸出資料夾
base_model = "meta-llama/Llama-3.1-8B-Instruct"
lora_path = "./outputs-qlora-llama3-8b"

# 載入 tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model)

# 載入基底模型（4-bit 量化）
model = AutoModelForCausalLM.from_pretrained(

    base_model,
    device_map="auto",
)

# 套用 LoRA 權重
model = PeftModel.from_pretrained(model, lora_path)

# 測試推論
prompt = "你是誰?"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=1024,
        do_sample=True,
        temperature=0.7,
    )

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
