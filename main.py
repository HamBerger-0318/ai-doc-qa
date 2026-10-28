from fastapi import FastAPI

# 这就是你的服务器实例，现代工程都这么写
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, 这是我的第一个FastAPI接口"}

@app.post("/chat")
def chat_with_ai(question: str):
    # 这里我们暂时用一句话模拟你的RAG
    # 明天我们会把真实的DeepSeek接进来
    return {
        "your_question": question,
        "ai_answer": f"我收到了你的问题：{question}。我正在慢慢学习如何回答。"
    }