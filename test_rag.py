import os
from openai import OpenAI
import chromadb
from my_tools import read_file

# 1. 初始化
sf_client = OpenAI(api_key=os.getenv("SILICONFLOW_KEY"), base_url="https://api.siliconflow.cn/v1")
ds_client = OpenAI(api_key=os.getenv("DEEPSEEK_KEY"), base_url="https://api.deepseek.com")
chroma_client = chromadb.PersistentClient(path="./my_vector_db_cli")
collection = chroma_client.get_or_create_collection(name="cli_knowledge")

def process_file(file_path):
    print(f"正在处理文件: {file_path} ...")
    full_text = read_file(file_path)
    if not full_text:
        print("文件内容为空，处理失败。")
        return

    chunks = [full_text[i:i+500] for i in range(0, len(full_text), 500)]
    
    try:
        chroma_client.delete_collection("cli_knowledge")
    except Exception:
        pass
    global collection
    collection = chroma_client.get_or_create_collection(name="cli_knowledge")

    print(f"正在向量化，共 {len(chunks)} 块...")
    for i in range(0, len(chunks), 10):
        batch = chunks[i:i+10]
        emb_list = sf_client.embeddings.create(model="BAAI/bge-m3", input=batch).data
        for j, emb_data in enumerate(emb_list):
            collection.add(ids=[f"id_{i+j}"], embeddings=[emb_data.embedding], documents=[batch[j]])
    print("✅ 文件处理完成！\n")

# 👇 注意这里！函数多接收了一个叫 history 的本子
def ask_question(prompt, history):
    question_emb = sf_client.embeddings.create(model="BAAI/bge-m3", input=prompt).data[0].embedding
    results = collection.query(query_embeddings=[question_emb], n_results=2)
    
    if not results['documents'] or not results['documents'][0]:
        return "数据库里没有内容，请先处理文件。"

    context = "\n\n---\n\n".join(results['documents'][0])

    # 👇 核心魔法在这里：把所有东西塞进一个列表
    messages_to_send = [
        {"role": "system", "content": "你是文档助手。请严格根据提供的文档片段回答问题。"}
    ]
    
    # 👇 把“小本本”里的历史记录，全部倒进这个列表里
    messages_to_send.extend(history) 
    
    # 👇 最后加上你刚刚问的这句话
    messages_to_send.append({"role": "user", "content": f"文档片段：\n{context}\n\n问题：{prompt}"})

    response = ds_client.chat.completions.create(
        model="deepseek-chat",
        messages=messages_to_send
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    # 这里写你电脑里真实存在的文件名！比如 paper.pdf
    process_file("paper.pdf") 

    # 👇 准备一个空小本本
    history = [] 
    
    print("🤖 AI助手已上线！输入问题开始对话（输入 '退出' 结束）：")
    while True:
        user_input = input("\n你: ")
        if user_input == "退出":
            print("再见！")
            break
        if not user_input.strip():
            continue
        
        print("AI思考中...")
        
        # 👇 把小本本传进去
        answer = ask_question(user_input, history)
        print(f"AI: {answer}")
        
        # 👇 问完了，把你说的话和AI的回答，都记在小本本上
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": answer})c