# 我的AI文档助手 (RAG应用)
## 🌐 在线体验地址
👉 **[点击这里，立刻使用我的 AI 文档助手](https://ai-doc-app-f49rouhkwwtl97fo2tkxjk.streamlit.app/)**
## 项目简介
基于大模型和向量数据库的本地知识库系统，支持网页端（Streamlit）和终端纯后端（CLI）两种交互模式。实现了多文件批量解析、多轮对话记忆、跨文档综合问答。


##学习笔记
**API**本质类似自来水厂，前后端分别负责request和response
**本地服务** ：使用python自带的HTTP.server或手写底层代码，能在本地（localhost）启动一个服务，通过端口（8000）供浏览器访问
**数据交互**：网络数据传输通常使用json格式，后端将数据打包成json格式返回给前端
## 核心架构 (RAG = 开卷考试)
```mermaid
graph TD
    A[用户上传PDF/TXT] --> B(my_tools.py: 读取文本)
    B --> C[文本切块 Chunking]
    C --> D[调用 硅基流动 API: 打指纹]
    D --> E[(存入 Chroma 向量数据库)]
    
    F[用户输入问题] --> G[调用 硅基流动 API: 问题打指纹]
    G --> H[去 Chroma 搜索最相似的块]
    H --> I[拼接历史记录 History]
    I --> J[调用 DeepSeek API: 生成回答]
    J --> K[网页端显示答案]
