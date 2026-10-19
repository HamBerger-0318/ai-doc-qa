# 我的AI文档助手 (RAG应用)

## 项目简介
基于大模型和向量数据库的本地知识库系统。支持多文件批量解析、跨文件综合问答。

## 核心功能
- **多文件批量处理**：支持同时上传多个 PDF/TXT 文件，合并处理。
- **跨文件问答**：系统可将多个文件内容统一向量化，实现跨文档的关联查询。
- **动态参数调节**：前端提供 Slider 滑块，用户可实时调整文本切块大小（Chunk Size）。
- **系统清理机制**：支持一键清空聊天记录；读取完毕后自动清理本地临时文件，防止内存泄漏。
- **数据安全**：使用环境变量（os.getenv）读取 API Key，杜绝密钥泄露风险。

## 技术栈
- 前端界面：Streamlit
- 大模型调用：DeepSeek API
- 文本向量化：SiliconFlow (BAAI/bge-m3)
- 向量数据库：ChromaDB
- 文本解析：PyPDF

## 怎么运行？
1. 安装依赖：`pip install streamlit openai pypdf chromadb numpy`
2. 配置环境变量：`DEEPSEEK_KEY` 和 `SILICONFLOW_KEY`
3. 启动程序：`python -m streamlit run app.py`