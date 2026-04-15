import gc

import torch

from codes.util.qwen3_util import load_qwen3_model, qwen3_ask

model, tokenizer = load_qwen3_model(model_name="Qwen/Qwen3.5-4B")

gc.collect()
torch.cuda.empty_cache()

result = qwen3_ask("你可以解釋程式碼異味嗎", model, tokenizer)[0]

print("content: \n", result)