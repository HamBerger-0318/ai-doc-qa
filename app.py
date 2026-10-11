import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
import chromadb

# 页面设置
st.set_page_config(page_title="我的AI文档助手", page_icon="📚")
st.title("📚 我的AI文档助手")

# ================= 配置你的两把钥匙 =================
DEEPSEEK_KEY = "sk-" 
SILICONFLOW_KEY = "sk-"
# ===================================================

# 初始化客户端
sf_client = OpenAI(api_key=SILICONFLOW_KEY, base_url="https://api.siliconflow.cn/v1")
ds_client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")

# 设置数据库
chroma_client = chromadb.PersistentClient(path="./my_vector_db")
collection = chroma_client.get_or_create_collection(name="pdf_knowledge")

# 侧边栏：上传PDF
with st.sidebar:
    st.header("上传文档")
    uploaded_file = st.file_uploader("请选择PDF文件", type="pdf")
    
    if uploaded_file is not None:
        if st.button("处理这份新文档"):
            # 保存上传的文件
            with open("test.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 读取并切块
            reader = PdfReader("test.pdf")
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text: full_text += text
            
            chunks = [full_text[i:i+500] for i in range(0, len(full_text), 500)]
            
            # 清空旧数据，存入新数据
            chroma_client.delete_collection("pdf_knowledge")
            collection = chroma_client.get_or_create_collection(name="pdf_knowledge")
            
            st.write(f"正在处理文档，共 {len(chunks)} 块...")
            for i in range(0, len(chunks), 10):
                batch = chunks[i:i+10]
                emb_list = sf_client.embeddings.create(model="BAAI/bge-m3", input=batch).data
                for j, emb_data in enumerate(emb_list):
                    collection.add(ids=[f"id_{i+j}"], embeddings=[emb_data.embedding], documents=[batch[j]])
            st.success("文档处理完成！可以开始提问了。")

# 主界面：聊天窗口
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史聊天记录
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
            # 搜索相关段落
            question_emb = sf_client.embeddings.create(model="BAAI/bge-m3", input=prompt).data[0].embedding
            results = collection.query(query_embeddings=[question_emb], n_results=2)
            context = "\n\n---\n\n".join(results['documents'][0])
            
            # 生成回答
            response = ds_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是文档助手。请严格根据提供的文档片段回答问题。"},
                    {"role": "user", "content": f"文档片段：\n{context}\n\n问题：{prompt}"}
                ]
            )
            answer = response.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})