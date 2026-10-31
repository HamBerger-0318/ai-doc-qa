# 📚 我的 AI 文档助手 (RAG 应用)

基于大模型与向量数据库构建的本地知识库系统，支持多文件解析与跨文档问答。

## 🌐 在线体验地址
👉 **[点击这里，立刻使用我的 AI 文档助手](https://ai-doc-app-f49rouhkwwtl97fo2tkxjk.streamlit.app/)**

## 🛠️ 技术栈
*   **前端交互**：Streamlit (已部署至公网)
*   **后端接口**：FastAPI (实现 RESTful API 接口)
*   **大语言模型**：DeepSeek API
*   **文本向量化**：SiliconFlow (BAAI/bge-m3)
*   **向量数据库**：ChromaDB

## ✨ 核心功能
- [x] 支持多文件（PDF/TXT）批量上传
- [x] 动态调节切块大小 (Chunk Size)
- [x] 跨文档综合检索问答
- [x] 对话历史溯源展示
- [x] 临时文件读取后自动清理