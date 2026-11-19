import streamlit as st
import os
import requests
from openai import OpenAI
from pypdf import PdfReader
import chromadb
from my_tools import read_file

# 本地开发时自动读 .env（装了 python-dotenv 才生效，没装就跳过）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 页面设置
st.set_page_config(page_title="我的AI文档助手", page_icon="📚")
st.title("📚 我的AI文档助手")

# ===================== 密钥读取 =====================
# 本地：环境变量 / .env；Streamlit Cloud：secrets。两边都能读到。
def secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

SILICONFLOW_KEY = secret("SILICONFLOW_KEY")
# ====================================================

# 初始化客户端
sf_client = OpenAI(api_key=SILICONFLOW_KEY, base_url="https://api.siliconflow.cn/v1")

# 设置数据库
chroma_client = chromadb.PersistentClient(path="./my_vector_db")
collection = chroma_client.get_or_create_collection(name="pdf_knowledge")

# 侧边栏：上传PDF
with st.sidebar:
    st.header("上传文档")
    chunk_size = st.slider("选择文本切块大小", min_value=100, max_value=1000, value=500, step=50)
    uploaded_files = st.file_uploader("请选择PDF或TXT文件", type=["pdf", "txt"], accept_multiple_files=True)
    st.divider()
    
    if st.button("清空聊天记录"):
        st.session_state.messages = []
        st.rerun()
        
    if uploaded_files:
        if st.button("处理这份新文档"):
            full_text = ""
            try:
                chroma_client.delete_collection("pdf_knowledge")
            except Exception:
                pass
            collection = chroma_client.get_or_create_collection(name="pdf_knowledge")
            
            for file in uploaded_files:
                ext = os.path.splitext(file.name)[1]
                file_path = f"uploaded_file{ext}"
                with open(file_path, "wb") as f:  
                    f.write(file.getbuffer())
                try:
                    file_text = read_file(file_path)
                except Exception as e:
                    st.error(f"文件处理出错啦喵！：{e}")
                    file_text = ""
                if file_text:
                    full_text += file_text + "\n\n---\n\n"  
                    os.remove(file_path)  
                    
            if full_text:
                st.write(f"当前总字数，共 {len(full_text)} 字。")
                chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
                st.write(f"正在处理文档，共 {len(chunks)} 块...")
                for i in range(0, len(chunks), 10):
                    batch = chunks[i:i+10]
                    emb_list = sf_client.embeddings.create(model="BAAI/bge-m3", input=batch).data
                    for j,emb_data in enumerate(emb_list):
                        collection.add(ids=[f"chunk_{i+j}"], embeddings=[emb_data.embedding], documents=[batch[j]])
                st.success(f"处理完成！共合并 {len(uploaded_files)} 个文件，切成了 {len(chunks)} 块。")
            else:
                st.error("您上传的文件里没有文字，请换一个有内容的文件喵！")

# 主界面：聊天窗口
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("针对文档提问..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if collection.count() == 0:
            st.write("数据库为空，请先在左侧上传PDF哦！")
        else:
            # 1. 前端自己查库，拿到片段
            question_emb = sf_client.embeddings.create(model="BAAI/bge-m3", input=prompt).data[0].embedding
            results = collection.query(query_embeddings=[question_emb], n_results=2)
            context_snippets = results['documents'][0]
             
            # 2. 把问题 + 片段发给后端，只接后端的 answer
            try:
                response = requests.post(
                    f"{secret('BACKEND_URL')}/ask",
                    json={"question": prompt, "context": context_snippets},
                    headers={"x-token": secret("API_TOKEN")},   # ← 带上暗号，没它后端直接 401
                    timeout=30
                )
                if response.status_code == 200:
                    st.markdown(response.json()["answer"])
                elif response.status_code == 401:
                    st.error("暗号不对：前端的 API_TOKEN 和后端不一致。")
                elif response.status_code == 413:
                    st.error("内容太长，被后端拦下了。")
                else:
                    st.error(f"后端报错，状态码：{response.status_code}")
            except Exception as e:
                st.error(f"❌ 连不上后端，检查 Docker 和隧道。报错：{e}")
            
            # 3. 展示前端自己查到的原文片段
            if context_snippets:
                with st.expander("查看检索到的原文片段"):
                    for i, doc in enumerate(context_snippets): 
                        st.markdown(f"片段 {i+1}:\n\n")
                        st.write(doc)
                        st.write("---")