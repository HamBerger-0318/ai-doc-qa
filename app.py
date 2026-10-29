import streamlit as st#python前端书写工具
import os
from openai import OpenAI
from pypdf import PdfReader
import chromadb#导入一个向量数据库的包
from my_tools import read_file#导入自定义的读取文件的函数
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
    #1滑块组件
    chunk_size =st.slider("选择文本切块大小", min_value=100, max_value=1000, value=500, step=50)
    #2多文件上传组件
    uploaded_files =st.file_uploader("请选择PDF或TXT文件", type=["pdf", "txt"], accept_multiple_files=True)
    st.divider()#加一条分割线
    #3清空聊天记录按钮
    if st.button("清空聊天记录"):
        st.session_state.messages = []
        st.rerun()#意思是立即刷新页面，重新运行脚本
    if uploaded_files:
        if st.button("处理这份新文档"):
            full_text = ""
            try:
                chroma_client.delete_collection("pdf_knowledge")
            except Exception:
                pass
            collection = chroma_client.get_or_create_collection(name="pdf_knowledge")
            for file in uploaded_files:#挨个处理每个上传的文件
                ext=os.path.splitext(file.name)[1]
                # 保存上传的文件    
                file_path = f"uploaded_file{ext}"
                with open(file_path, "wb") as f:  
                    f.write(file.getbuffer())
                try:
                    file_text = read_file(file_path)
                except Exception as e:
                    st.error(f"文件处理出错啦喵！：{e}")
                    file_text = ""
                # 读取并切块
                if file_text:
                    full_text += file_text + "\n\n---\n\n"  # 合并文件内容并添加分隔符
                    os.remove(file_path)  # 删除临时保存的文件
            if full_text:#所有文件读取成功后，才进行切块和存入向量数据库
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
                st.error("您上传的文件里没有文字(可能是空文件或图片),请换一个有内容的文件喵！")
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
            with st.expander("查看检索到的原文片段"):
                for i, doc in enumerate(results['documents'][0]):
                    st.markdown(f"片段 {i+1}:\n\n")
                    st.write(doc)
                    st.write("---")
