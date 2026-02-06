from codes.util.llama3_util import load_llama3_model, llama3_ask
from codes.util.faiss_util import search_docs

# 查詢問題
query = "審核 API 要用甚麼規則?"
filter_by_threshold = False

retrieved_docs, filtered_results = search_docs(query=query, threshold=filter_by_threshold)

llm_pipeline, tokenizer = load_llama3_model()

prompt = f"根據以下規則回答問題：\n{retrieved_docs}\n\n問題：{query}\n回答："

result = llama3_ask("", prompt, llm_pipeline)
result = result[0]["generated_text"][-1]["content"]

if filter_by_threshold:
    print("符合閾值的文件：")
    for r in filtered_results:
        print(f"Doc: {r['doc']}, 相似度: {r['score']:.4f}")

print("=== 查詢結果 ===")
print(result)
