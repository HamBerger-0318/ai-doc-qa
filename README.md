# AI 文档问答系统 (ai-doc-qa)

## 项目介绍
这是一个用 Python 写的 AI 小工具。上传一份 PDF，它就能根据 PDF 的内容回答你的问题。

## 使用技术
- Python
- DeepSeek 大模型 API
- 硅基流动 Embedding API
- ChromaDB 向量数据库
- Streamlit 网页界面

## 怎么运行？
1. 安装依赖：`pip install openai pypdf chromadb streamlit`
2. 运行程序：`python -m streamlit run app.py`