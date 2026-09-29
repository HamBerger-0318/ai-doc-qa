from openai import OpenAI
from pypdf import PdfReader
import chromadb

# ================= 配置你的两把钥匙 =================
DEEPSEEK_KEY = "sk-2180263b7dd645b6bc38309f227728e5"
SILICONFLOW_KEY = "sk-srmajmaoglnujsaboigwhsyaphvnusakopxsaakigceqican"
# ===================================================

# 1. 初始化向量数据库（本地文件夹，存了以后就不用重复计算了）
chroma_client = chromadb.PersistentClient(path="./my_vector_db")
collection = chroma_client.get_or_create_collection(name="pdf_knowledge")

# 2. 检查数据库里有没有数据，没有才去读PDF
if collection.count() == 0:
    print("检测到数据库为空，开始读取PDF并打指纹...")
    reader = PdfReader("paper.pdf")
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text

    # 把文字切成每500个字一块（这次不限制数量了！）
    chunks = [full_text[i:i+500] for i in range(0, len(full_text), 500)]
    
    sf_client = OpenAI(
        api_key=SILICONFLOW_KEY,
        base_url="https://api.siliconflow.cn/v1"
    )
    
    # 分批打指纹，存入数据库
    batch_size = 10
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        emb_list = sf_client.embeddings.create(
            model="BAAI/bge-m3",
            input=batch
        ).data
        for j, emb_data in enumerate(emb_list):
            collection.add(
                ids=[f"id_{i+j}"],
                embeddings=[emb_data.embedding],
                documents=[batch[j]]
            )
    print(f"处理完成！共存入 {collection.count()} 块内容。")
else:
    print(f"数据库已有数据，共 {collection.count()} 块内容，直接开始提问！")

# 3. 开始问答
question = "这篇文档主要讲了什么？"
print(f"\n你的问题是：{question}")

# 把问题打上指纹
sf_client = OpenAI(api_key=SILICONFLOW_KEY, base_url="https://api.siliconflow.cn/v1")
question_emb = sf_client.embeddings.create(
    model="BAAI/bge-m3",
    input=question
).data[0].embedding

# 4. 去数据库里搜最像的2块
results = collection.query(
    query_embeddings=[question_emb],
    n_results=2
)
best_chunks = results['documents'][0]

# 5. 交给 DeepSeek 生成回答
ds_client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")
context = "\n\n---\n\n".join(best_chunks)

response = ds_client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个文档助手。请严格根据用户提供的文档片段回答问题，不要编造。"},
        {"role": "user", "content": f"文档片段如下：\n{context}\n\n问题：{question}"}
    ]
)

print("\n=== AI 回答 ===")
print(response.choices[0].message.content)