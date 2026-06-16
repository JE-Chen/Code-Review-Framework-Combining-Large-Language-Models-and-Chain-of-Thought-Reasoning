import gc

import torch

from codes.util.hf_model_util import load_hf_model, hf_generate

model, tokenizer = load_hf_model(model_name="Qwen/Qwen3.5-4B")

gc.collect()
torch.cuda.empty_cache()

result = hf_generate("你可以解釋程式碼異味嗎", model, tokenizer)[0]

print("content: \n", result)