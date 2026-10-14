import streamlit as st#python前端书写工具
import os
from openai import OpenAI
from pypdf import PdfReader
import chromadb#导入一个向量数据库的包

# 页面设置
st.set_page_config(page_title="我的AI文档助手", page_icon="📚")
st.title("📚 我的AI文档助手")

# ================= 配置你的两把钥匙 =================
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")  # 从环境变量中获取DeepSeek API Key
SILICONFLOW_KEY = os.getenv("SILICONFLOW_KEY")  # 从环境变量中获取SiliconFlow API Key
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
    uploaded_file = st.file_uploader("请选择PDF或TXT文件", type=["pdf", "txt"])

    if uploaded_file is not None:
        if st.button("处理这份新文档"):
            # 保存上传的文件
            file_path = "uploaded_file.tmp"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 读取并切块
            #判断是否为pdf文件，如果是就用pypdf读取，否则就用普通的文本读取
            if uploaded_file.name.lower().endswith(".pdf"):
                try:
                    reader = PdfReader(file_path)
                    full_text = ""
                    #循环的读取每一页的内容
                    for page in reader.pages:
                        text = page.extract_text()
                        print("我正在读第",page,"页")
                        if text:
                            full_text += text
                except Exception as e:
                    st.error(f"读取 PDF 失败: {e}")
                    full_text = ""
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    full_text = f.read()
                #将数据也就是读取的文字按500字切块，存入向量数据库
            if full_text:
                chunks = [full_text[i:i+500] for i in range(0, len(full_text), 500)]

                try:
                    chroma_client.delete_collection("pdf_knowledge")
                except Exception:
                    pass
                collection = chroma_client.get_or_create_collection(name="pdf_knowledge")
#讲切块后的数据分批存入向量数据
                st.write(f"正在处理文档，共 {len(chunks)} 块...")
                for i in range(0, len(chunks), 10):
                    batch = chunks[i:i+10]
                    #生成一个数字指纹导入到emb-list中
                    emb_list = sf_client.embeddings.create(model="BAAI/bge-m3", input=batch).data
                    for j, emb_data in enumerate(emb_list):
                        collection.add(ids=[f"id_{i+j}"], embeddings=[emb_data.embedding], documents=[batch[j]])
                st.success("文档处理完成！可以开始提问了。")
            else:
                st.warning("没有读取到有效文本，请检查文件内容。")

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