# RAG检索流程

> 文档版本：v1.0  
> 更新时间：2026-05-28  
> 核心模块：`server/modules/rag/`

---

## 目录

- [一、流程概述](#一流程概述)
- [二、完整流程图](#二完整流程图)
- [三、模块化架构](#三模块化架构)
- [四、知识库选择策略](#四知识库选择策略)
- [五、检索与生成](#五检索与生成)
- [六、关键代码路径](#六关键代码路径)

---

## 一、流程概述

RAG（检索增强生成）流程用于从知识库检索相关文档，增强LLM回答质量：

| 步骤 | 功能 | 模块 |
|------|------|------|
| **路由判断** | 判断是否需要检索 | `RouterNode` |
| **知识库选择** | 选择最合适的知识库 | `select_knowledge_base` |
| **文档检索** | 向量检索相关文档 | `retrieve` |
| **上下文注入** | 将文档注入到Prompt | `ContextBuilder` |

---

## 二、完整流程图

```mermaid
flowchart TB
    subgraph Phase1["阶段1: 路由判断"]
        A[用户查询] --> B[RouterNode]
        B --> C[should_retrieve]
        C --> D{需要检索?}
        D -->|否| E[跳过RAG]
        D -->|是| F[进入检索流程]
    end
    
    subgraph Phase2["阶段2: 知识库选择"]
        F --> G[select_knowledge_base]
        G --> H[遍历知识库列表]
        H --> I[计算匹配度]
        I --> J[选择最佳知识库]
        J --> K[switch_knowledge_base]
    end
    
    subgraph Phase3["阶段3: 文档检索"]
        K --> L[retrieve]
        L --> M[向量检索]
        M --> N[返回文档列表]
        N --> O[存入 state.documents]
    end
    
    subgraph Phase4["阶段4: 上下文注入"]
        O --> P[ContextBuilder]
        P --> Q[构建增强Prompt]
        Q --> R[注入RAG文档]
        R --> S[传递给 Agent]
    end
    
    E --> S
    S --> T[生成最终回答]
    
    style A fill:#e1f5fe,color:#01579b
    style F fill:#c8e6c9,color:#1a5e20
    style J fill:#fff3e0,color:#e65100
    style O fill:#f3e5f5,color:#7b1fa2
    style T fill:#bbdefb,color:#0d47a1
```

---

## 三、模块化架构

### 3.1 RAGWorkflow 组件结构

```mermaid
flowchart TB
    subgraph RAGWorkflow["RAGWorkflow 模块化架构"]
        A[RAGWorkflow] --> B[Indexer<br/>索引器]
        A --> C[Retriever<br/>检索器]
        A --> D[Generator<br/>生成器]
        
        B --> E[文档分块]
        B --> F[向量编码]
        B --> G[索引存储]
        
        C --> H[查询编码]
        C --> I[相似度搜索]
        C --> J[结果过滤]
        
        D --> K[Prompt构建]
        D --> L[LLM调用]
        D --> M[回答生成]
    end
    
    style RAGWorkflow fill:#e1f5fe,color:#01579b
```

### 3.2 可插拔组件设计

| 组件 | 接口 | 可替换实现 |
|------|------|------------|
| **Indexer** | `index(documents)` | FAISS, Chroma, Pinecone |
| **Retriever** | `retrieve(query, k)` | 向量检索, BM25, 混合检索 |
| **Generator** | `generate(query, documents)` | OpenAI, Claude, 本地模型 |

---

## 四、知识库选择策略

### 4.1 知识库匹配流程

```mermaid
flowchart LR
    subgraph KBSelect["知识库选择"]
        A[用户查询] --> B[提取关键词]
        B --> C[遍历知识库]
        C --> D{关键词匹配?}
        D -->|匹配| E[计算匹配度]
        D -->|不匹配| F[继续遍历]
        E --> G[选择最高匹配度]
        F --> C
        G --> H[返回知识库名称]
    end
    
    style KBSelect fill:#c8e6c9,color:#1a5e20
```

### 4.2 知识库类型

| 知识库 | 适用场景 | 关键词 |
|--------|----------|--------|
| **product_docs** | 产品文档 | 产品, 功能, 使用 |
| **tech_docs** | 技术文档 | 技术, API, 开发 |
| **faq** | 常见问题 | 问题, 帮助, FAQ |

---

## 五、检索与生成

### 5.1 向量检索流程

```mermaid
flowchart TB
    subgraph VectorSearch["向量检索流程"]
        A[用户查询] --> B[Query Encoder]
        B --> C[查询向量]
        C --> D[Vector Store]
        D --> E[相似度计算]
        E --> F[Top-K 文档]
        F --> G[过滤低相关性]
        G --> H[返回文档列表]
    end
    
    style VectorSearch fill:#fff3e0,color:#e65100
```

### 5.2 上下文注入流程

```mermaid
flowchart TB
    subgraph ContextInject["上下文注入"]
        A[任务描述] --> B[ContextBuilder]
        B --> C[获取 documents]
        C --> D{有文档?}
        D -->|有| E[构建上下文 Prompt]
        D -->|无| F[使用原始 Prompt]
        E --> G[格式化文档内容]
        G --> H[拼接: 任务 + 文档]
        H --> I[返回增强 Prompt]
    end
    
    style ContextInject fill:#f3e5f5,color:#7b1fa2
```

**上下文Prompt模板**：

```
参考文档：
{document_1}
{document_2}
...

任务：{task_description}

请根据参考文档完成上述任务。
```

---

## 六、关键代码路径

| 步骤 | 文件 | 关键函数 |
|------|------|----------|
| 路由判断 | [nodes/rag.py](file:///d:/办公/AI/langgraph-agent/server/modules/langgraph/nodes/rag.py) | `RouterNode.__call__()` |
| 知识库选择 | [rag_workflow.py](file:///d:/办公/AI/langgraph-agent/server/modules/rag/rag_workflow.py) | `select_knowledge_base()` |
| 文档检索 | [nodes/rag.py](file:///d:/办公/AI/langgraph-agent/server/modules/langgraph/nodes/rag.py) | `RetrieveNode.__call__()` |
| 上下文构建 | [context_builder.py](file:///d:/办公/AI/langgraph-agent/server/modules/langgraph/context_builder.py) | `ContextBuilder.build_task_with_context()` |

---

## 相关文档

- [LangGraph状态图总览](./LangGraph状态图总览.md)
- [Plan模式流程](./Plan模式流程.md)
- [Direct模式流程](./Direct模式流程.md)