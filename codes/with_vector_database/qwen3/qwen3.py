from codes.util.qwen3_util import load_qwen3_model, qwen3_ask
from codes.with_vector_database.utils.faiss_util import search_docs

# 查詢問題
query = "審核 API 要用甚麼規則?"
filter_by_threshold = False

retrieved_docs, filtered_results = search_docs(query=query, filter_by_threshold=filter_by_threshold)

# 載入 Qwen 的生成模型，用來生成答案
gen_tokenizer, gen_model = load_qwen3_model()

# 建立提示詞，把檢索到的文件和問題一起丟給生成模型
prompt = f"根據以下規則回答問題：\n{retrieved_docs}\n\n問題：{query}\n回答："

# 呼叫生成模型，產生回答
result = qwen3_ask("", prompt, gen_tokenizer, gen_model, max_new_tokens=32768)[0]

if filter_by_threshold:
    print("符合閾值的文件：")
    for r in filtered_results:
        print(f"Doc: {r['doc']}, 相似度: {r['score']:.4f}")

print("=== 查詢結果 ===")
print(result)
