import os
from openai import OpenAI
import chromadb
from my_tools import read_file  # 导入你自己的切菜工

# 1. 初始化客户端（这里没有任何 st 代码！）
sf_client = OpenAI(api_key=os.getenv("SILICONFLOW_KEY"), base_url="https://api.siliconflow.cn/v1")
ds_client = OpenAI(api_key=os.getenv("DEEPSEEK_KEY"), base_url="https://api.deepseek.com")

chroma_client = chromadb.PersistentClient(path="./my_vector_db_cli")
collection = chroma_client.get_or_create_collection(name="cli_knowledge")

def process_file(file_path):
    #文件处理流水线，读-切-打指纹-入库。
    print(f"正在处理文件: {file_path} ...")
    full_text = read_file(file_path)#读
    if not full_text:
        print("文件内容为空，处理失败。")
        return

    # 切块
    chunks = [full_text[i:i+500] for i in range(0, len(full_text), 500)]
    
    # 清空旧数据
    try:
        chroma_client.delete_collection("cli_knowledge")
    except Exception:
        pass
    global collection
    collection = chroma_client.get_or_create_collection(name="cli_knowledge")

    # 打指纹入库
    print(f"正在向量化，共 {len(chunks)} 块...")
    for i in range(0, len(chunks), 10):
        batch = chunks[i:i+10]
        emb_list = sf_client.embeddings.create(model="BAAI/bge-m3", input=batch).data
        for j, emb_data in enumerate(emb_list):
            collection.add(ids=[f"id_{i+j}"], embeddings=[emb_data.embedding], documents=[batch[j]])
    print("✅ 文件处理完成，已存入数据库！\n")

def ask_question(prompt):
   
    # 向量化问题
    question_emb = sf_client.embeddings.create(model="BAAI/bge-m3", input=prompt).data[0].embedding
    # 检索
    results = collection.query(query_embeddings=[question_emb], n_results=2)#去数据库里找最相似片段
    
    if not results['documents'] or not results['documents'][0]:
        return "数据库里没有内容，请先处理文件。"

    context = "\n\n---\n\n".join(results['documents'][0])

    # 生成回答，把问题和片段发给大模型生成回答
    response = ds_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            #Chat Completions API 规范。
            {"role": "system", "content": "你是文档助手。请严格根据提供的文档片段回答问题。"},
            {"role": "user", "content": f"文档片段：\n{context}\n\n问题：{prompt}"}
        ]
    )
    return response.choices[0].message.content

# ================= 纯终端交互区 =================
if __name__ == "__main__":
    # 先处理一下文件（你可以改成你文件夹里的文件名）
    #负责接收用户输入和调度的主程序
    process_file("test.pdf") 

    print("🤖 AI助手已上线！输入问题开始对话（输入 '退出' 结束）：")
    while True:
        user_input = input("\n你: ")
        if user_input == "退出":
            print("再见！")
            break
        if not user_input.strip():
            continue
        
        print("AI思考中...")
        answer = ask_question(user_input)
        print(f"AI: {answer}")