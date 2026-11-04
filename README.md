# 📚 我的 AI 文档助手 (RAG 应用)

基于大语言模型（LLM）与向量数据库构建的本地知识库系统。支持多文件批量解析、跨文档综合问答、检索溯源，并实现了前端交互、后端 API 以及 Docker 容器化部署的完整全栈闭环。

## 🌐 在线体验地址
👉 **[点击这里，立刻使用我的 AI 文档助手](https://ai-doc-app-f49rouhkwwtl97fo2tkxjk.streamlit.app/)**
*(注：由于免费云服务器资源限制，冷启动可能需要几秒钟。)*

## ✨ 核心功能
- **多文件批量处理**：支持同时上传多个 PDF 与 TXT 文件，合并解析。
- **跨文件问答与溯源**：系统统一向量化，支持跨文档检索，并在前端展示命中的原始文档片段。
- **动态参数调节**：前端提供 Slider 滑块，支持实时调整文本切块大小（Chunk Size），直观体验 RAG 检索差异。
- **数据安全与隔离**：全链路使用环境变量/Secrets 读取 API Key；上传文件读取后自动清理，防止内存泄漏。

## 🛠️ 技术栈
- **前端界面**：Streamlit (已部署至 Streamlit Cloud)
- **后端接口**：FastAPI + Uvicorn (已实现 Docker 容器化)
- **大语言模型**：DeepSeek API
- **文本向量化**：SiliconFlow (BAAI/bge-m3 模型)
- **向量数据库**：ChromaDB
- **文档解析**：PyPDF

## 🏗️ 系统架构
```mermaid
graph TD
    A[用户上传 PDF/TXT] --> B(文本解析与切块)
    B --> C(调用 SiliconFlow API 向量化)
    C --> D[(ChromaDB 向量数据库)]
    
    E[用户提问] --> F(FastAPI 后端接口)
    F --> G(检索相似片段)
    G --> D
    G --> H(结合上下文与 Prompt)
    H --> I(调用 DeepSeek 大模型)
    I --> J(返回回答与原文溯源)