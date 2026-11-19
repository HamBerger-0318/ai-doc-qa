import os
from typing import List, Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from openai import OpenAI

# 自动读取同目录下的 .env（装了 python-dotenv 才生效，没装就跳过，不会报错）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI(title="我的RAG系统API")

# 模型客户端：key 从环境变量读，绝不写死在代码里
ds_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_KEY"),
    base_url="https://api.deepseek.com",
)

# ===================== 两道锁 =====================
API_TOKEN = os.getenv("API_TOKEN")      # 锁 1：暗号，前端必须带
MAX_CONTEXT_CHARS = 8000                # 锁 2：单次 context 总字数上限
MAX_QUESTION_CHARS = 1000               #        单次问题字数上限
# ==================================================


class QuestionRequest(BaseModel):
    question: str
    context: List[str]


def check_token(x_token: Optional[str]) -> None:
    """暗号不对，直接挡在门外，连模型都不碰。"""
    if not API_TOKEN:
        # 服务端自己没配，属于部署错误，不是用户的问题
        raise HTTPException(status_code=500, detail="服务端未配置 API_TOKEN")
    if x_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="unauthorized")


@app.get("/health")
def health():
    """健康检查：给隧道/云平台探活用，不花钱。"""
    return {"status": "ok", "auth": bool(API_TOKEN)}


@app.post("/ask")
def ask_ai(
    request: QuestionRequest,
    x_token: Optional[str] = Header(default=None),
):
    # 锁 1：暗号
    check_token(x_token)

    # 锁 2：长度。不设这个，对方一次传十万字就能烧掉几十块
    if len(request.question) > MAX_QUESTION_CHARS:
        raise HTTPException(status_code=413, detail="问题太长")
    total_chars = sum(len(c) for c in request.context)
    if total_chars > MAX_CONTEXT_CHARS:
        raise HTTPException(
            status_code=413,
            detail=f"context 太长：{total_chars} 字，上限 {MAX_CONTEXT_CHARS}",
        )

    context_text = "\n\n---\n\n".join(request.context)

    try:
        resp = ds_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是文档助手。只依据提供的片段回答，找不到答案就说不知道。",
                },
                {
                    "role": "user",
                    "content": f"文档片段：\n{context_text}\n\n问题：{request.question}",
                },
            ],
            timeout=30,
        )
        return {"answer": resp.choices[0].message.content}
    except Exception as e:
        # 不裸奔 500，返回结构化错误方便前端显示
        raise HTTPException(status_code=502, detail=f"上游出错：{e}")
