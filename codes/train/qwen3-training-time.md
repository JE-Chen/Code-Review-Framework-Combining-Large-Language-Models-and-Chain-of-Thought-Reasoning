```
/home/nknul40s/miniconda3/envs/LLM_Research/bin/python /home/nknul40s/LLM_Research/codes/train/qwen3.py 
Loading checkpoint shards: 100%|██████████| 16/16 [00:19<00:00,  1.19s/it]
2026-01-02 10:38:34.837095 Model loaded
trainable params: 3,375,366,144 || all params: 33,907,488,768 || trainable%: 9.9546
The tokenizer has new PAD/BOS/EOS tokens that differ from the model config and generation config. The model config and generation config were aligned accordingly, being updated with the tokenizer's values. Updated tokens: {'bos_token_id': None, 'pad_token_id': 151643}.
  0%|          | 0/30 [00:00<?, ?it/s]`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`.
 33%|███▎      | 10/30 [1:39:18<2:52:43, 518.16s/it]{'loss': 1.8744, 'grad_norm': 1.0627000331878662, 'learning_rate': 0.00016473862847818277, 'epoch': 1.0}
 67%|██████▋   | 20/30 [3:18:33<1:27:13, 523.37s/it]{'loss': 0.739, 'grad_norm': 1.7368723154067993, 'learning_rate': 6.298618446600856e-05, 'epoch': 2.0}
100%|██████████| 30/30 [4:58:32<00:00, 526.32s/it]{'loss': 0.4805, 'grad_norm': 0.6403655409812927, 'learning_rate': 5.862042845640403e-07, 'epoch': 3.0}
{'train_runtime': 17943.535, 'train_samples_per_second': 0.101, 'train_steps_per_second': 0.002, 'train_loss': 1.0313124020894369, 'epoch': 3.0}
100%|██████████| 30/30 [4:59:03<00:00, 598.11s/it]
2026-01-02 15:38:47.059683 Training complete

Process finished with exit code 0
```