# 我的AI文档助手 (RAG应用)

## 项目简介
基于大模型和向量数据库的本地知识库系统，支持网页端（Streamlit）和终端纯后端（CLI）两种交互模式。实现了多文件批量解析、多轮对话记忆、跨文档综合问答。

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