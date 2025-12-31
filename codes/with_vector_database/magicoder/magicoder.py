from codes.util.magicoder_util import magicoder_ask, load_magicoder_model
from codes.with_vector_database.utils.faiss_util import search_docs

# 查詢問題
query = "審核 API 要用甚麼規則?"
filter_by_threshold = False

retrieved_docs, filtered_results = search_docs(query=query, filter_by_threshold=filter_by_threshold)

# 建立提示詞，把檢索到的文件和問題一起丟給生成模型
prompt = f"根據以下規則回答問題：\n{retrieved_docs}\n\n問題：{query}\n回答："

model, tokenizer, device = load_magicoder_model()

result = magicoder_ask(query, model, tokenizer, device)

if filter_by_threshold:
    print("符合閾值的文件：")
    for r in filtered_results:
        print(f"Doc: {r['doc']}, 相似度: {r['score']:.4f}")

print("=== 查詢結果 ===")
print(result)