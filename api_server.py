from fastapi import FastAPI
from pydantic import BaseModel
import os
from openai import OpenAI
import chromadb

# 1. 初始化你的老伙计们（FastAPI、大模型、数据库）
app = FastAPI(title="我的RAG系统API")
sf_client = OpenAI(api_key=os.getenv("SILICONFLOW_KEY"), base_url="https://api.siliconflow.cn/v1")
ds_client = OpenAI(api_key=os.getenv("DEEPSEEK_KEY"), base_url="https://api.deepseek.com")

chroma_client = chromadb.PersistentClient(path="./my_vector_db_cli")
collection = chroma_client.get_or_create_collection(name="cli_knowledge")

# 2. 规定一下前端传过来的数据格式（必须有个叫 question 的字段）
class QuestionRequest(BaseModel):
    question: str

# 3. 核心接口：接收问题，去数据库搜，让大模型答，返回JSON
@app.post("/ask")
def ask_ai(request: QuestionRequest):
    prompt = request.question
    
    # 把你的老代码搬过来：搜数据库
    question_emb = sf_client.embeddings.create(model="BAAI/bge-m3", input=prompt).data[0].embedding
    results = collection.query(query_embeddings=[question_emb], n_results=2)
    
    # 简单容错
    if not results['documents'] or not results['documents'][0]:
        return {"answer": "数据库里没有内容，请先处理文件。"}

    context = "\n\n---\n\n".join(results['documents'][0])

    # 把你的老代码搬过来：调 DeepSeek 生成回答
    response = ds_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是文档助手。"},
            {"role": "user", "content": f"文档片段：\n{context}\n\n问题：{prompt}"}
        ]
    )
    answer = response.choices[0].message.content
    
    # 直接返回一个字典，FastAPI 会自动帮你把它变成 JSON 格式！
    return {"answer": answer}