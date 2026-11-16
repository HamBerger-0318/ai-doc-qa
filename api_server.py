from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os
from openai import OpenAI

app = FastAPI(title="我的RAG系统API")
ds_client = OpenAI(api_key=os.getenv("DEEPSEEK_KEY"), base_url="https://api.deepseek.com")

# 接收前端传来的问题 和 前端查好的片段
class QuestionRequest(BaseModel):
    question: str
    context: List[str] 

@app.post("/ask")
def ask_ai(request: QuestionRequest):
    # 后端彻底告别数据库，直接拼凑发给大模型
    context_text = "\n\n---\n\n".join(request.context)

    response = ds_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是文档助手。"},
            {"role": "user", "content": f"文档片段：\n{context_text}\n\n问题：{request.question}"}
        ]
    )
    answer = response.choices[0].message.content
    
    return {"answer": answer}
