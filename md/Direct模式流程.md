# Direct模式流程（直接执行）

> 文档版本：v1.0  
> 更新时间：2026-05-28  
> 核心模块：`server/modules/langgraph/executors/`

---

## 目录

- [一、流程概述](#一流程概述)
- [二、完整流程图](#二完整流程图)
- [三、执行器架构](#三执行器架构)
- [四、各类执行器详解](#四各类执行器详解)
- [五、多意图处理](#五多意图处理)
- [六、关键代码路径](#六关键代码路径)
- [七、扩展指南](#七扩展指南)

---

## 一、流程概述

Direct模式用于处理**简单意图**（RAG/Skill/MCP），直接调用对应执行器：

| 意图类别 | 执行器 | 功能 |
|----------|--------|------|
| **RAG** | `RagExecutor` | 知识库检索 |
| **SKILL** | `SkillExecutor` | 技能执行 |
| **MCP** | `McpExecutor` | MCP工具调用 |

---

## 二、完整流程图

```mermaid
flowchart TB
    subgraph Phase1["阶段1: 意图识别"]
        A[用户查询] --> B[IntentRouter.route]
        B --> C[识别意图类别]
        C --> D{类别判断}
        D -->|RAG/Skill/MCP| E[返回 Intent 列表]
    end
    
    subgraph Phase2["阶段2: 路由决策"]
        E --> F[IntentRouterNode]
        F --> G{判断 execution_mode}
        G -->|全是简单意图| H[返回 direct]
    end
    
    subgraph Phase3["阶段3: 执行分发"]
        H --> I[ExecuteDirectNode]
        I --> J[ExecutorRegistry.execute_all]
        J --> K[遍历 intents]
        K --> L{获取 category}
        L -->|rag| M[RagExecutor.execute]
        L -->|skill| N[SkillExecutor.execute]
        L -->|mcp| O[McpExecutor.execute]
    end
    
    subgraph Phase4["阶段4: 结果收集"]
        M --> P[ExecutionResult]
        N --> P
        O --> P
        P --> Q[存入 intent_results]
    end
    
    subgraph Phase5["阶段5: 最终回答"]
        Q --> R[CallModelNode]
        R --> S[RefinerRegistry.refine]
        S --> T[生成最终回答]
        T --> U[返回给用户]
    end
    
    style A fill:#e1f5fe,color:#01579b
    style H fill:#c8e6c9,color:#1a5e20
    style J fill:#fff3e0,color:#e65100
    style P fill:#f3e5f5,color:#7b1fa2
    style U fill:#bbdefb,color:#0d47a1
```

---

## 三、执行器架构

### 3.1 执行器注册表（工厂模式）

```mermaid
flowchart TB
    subgraph Registry["ExecutorRegistry 工厂"]
        A[register] --> B[注册执行器类]
        B --> C[_executors Dict]
        D[build] --> E[根据 category 构建实例]
        E --> F[返回 BaseExecutor]
        G[execute] --> H[调用 executor.execute]
        H --> I[返回 ExecutionResult]
    end
    
    style Registry fill:#e1f5fe,color:#01579b
```

### 3.2 执行器类继承关系

```mermaid
classDiagram
    class BaseExecutor {
        <<abstract>>
        +execute(intent, context) ExecutionResult
        +validate_intent(intent) bool
    }
    
    class RagExecutor {
        +execute(intent, context) ExecutionResult
        +validate_intent(intent) bool
    }
    
    class SkillExecutor {
        +execute(intent, context) ExecutionResult
        +validate_intent(intent) bool
    }
    
    class McpExecutor {
        +execute(intent, context) ExecutionResult
        +validate_intent(intent) bool
    }
    
    BaseExecutor <|-- RagExecutor
    BaseExecutor <|-- SkillExecutor
    BaseExecutor <|-- McpExecutor
```

### 3.3 ExecutionResult 结构

```python
ExecutionResult(
    success=True,              # 是否成功
    content="检索结果...",     # 执行内容
    error=None,                # 错误信息（如有）
)
```

---

## 四、各类执行器详解

### 4.1 RagExecutor 流程

```mermaid
flowchart LR
    subgraph RagExec["RagExecutor 执行流程"]
        A[Intent] --> B[提取 target]
        B --> C[选择知识库]
        C --> D[RAGWorkflow.retrieve]
        D --> E[返回文档列表]
        E --> F[格式化为 ExecutionResult]
    end
    
    style RagExec fill:#c8e6c9,color:#1a5e20
```

### 4.2 SkillExecutor 流程

```mermaid
flowchart LR
    subgraph SkillExec["SkillExecutor 执行流程"]
        A[Intent] --> B[提取 target 技能名]
        B --> C[加载 SKILL.md]
        C --> D[匹配技能指令]
        D --> E[执行技能脚本]
        E --> F[返回执行结果]
        F --> G[格式化为 ExecutionResult]
    end
    
    style SkillExec fill:#fff3e0,color:#e65100
```

### 4.3 McpExecutor 流程

```mermaid
flowchart LR
    subgraph McpExec["McpExecutor 执行流程"]
        A[Intent] --> B[提取 target 工具名]
        B --> C[构建 MCP 请求]
        C --> D[调用 MCP 服务]
        D --> E[解析工具响应]
        E --> F[格式化为 ExecutionResult]
    end
    
    style McpExec fill:#f3e5f5,color:#7b1fa2
```

---

## 五、多意图处理

### 5.1 多意图执行流程

```mermaid
flowchart TB
    subgraph MultiIntent["多意图执行"]
        A[Intent 列表] --> B[遍历 intents]
        B --> C[Intent 1: RAG]
        C --> D[RagExecutor]
        D --> E[Result 1]
        B --> F[Intent 2: Skill]
        F --> G[SkillExecutor]
        G --> H[Result 2]
        E --> I[收集到 intent_results]
        H --> I
        I --> J[CallModelNode 汇总]
    end
    
    style MultiIntent fill:#bbdefb,color:#0d47a1
```

### 5.2 多意图示例

**用户输入**: "查询文档内容，然后画一个流程图"

```python
intents = [
    Intent(type="rag_query", category="RAG", content="查询文档内容", order=1),
    Intent(type="skill_execute", category="SKILL", content="画流程图", target="drawio-skill", order=2),
]
```

**执行顺序**: RAG检索 → Skill执行 → 结果汇总

---

## 六、关键代码路径

| 步骤 | 文件 | 关键函数 | 行号 |
|------|------|----------|------|
| 执行入口 | [execute.py](file:///d:/办公/AI/langgraph-agent/server/modules/langgraph/nodes/execute.py) | `ExecuteDirectNode.__call__()` | L22-55 |
| 执行器注册 | [registry.py](file:///d:/办公/AI/langgraph-agent/server/modules/langgraph/executors/registry.py) | `ExecutorRegistry.register()` | L20-35 |
| 执行器构建 | [registry.py](file:///d:/办公/AI/langgraph-agent/server/modules/langgraph/executors/registry.py) | `ExecutorRegistry.build()` | L37-55 |
| 执行分发 | [registry.py](file:///d:/办公/AI/langgraph-agent/server/modules/langgraph/executors/registry.py) | `ExecutorRegistry.execute_all()` | L127-154 |
| RAG执行 | [rag_executor.py](file:///d:/办公/AI/langgraph-agent/server/modules/langgraph/executors/rag_executor.py) | `RagExecutor.execute()` | - |
| Skill执行 | [skill_executor.py](file:///d:/办公/AI/langgraph-agent/server/modules/langgraph/executors/skill_executor.py) | `SkillExecutor.execute()` | - |
| MCP执行 | [mcp_executor.py](file:///d:/办公/AI/langgraph-agent/server/modules/langgraph/executors/mcp_executor.py) | `McpExecutor.execute()` | - |

---

## 七、扩展指南

### 7.1 新增执行器

```python
# 1. 创建新执行器类
class WebSearchExecutor(BaseExecutor):
    def execute(self, intent: Dict, context: Dict) -> ExecutionResult:
        query = intent.get("content")
        results = self._search_engine.search(query)
        return ExecutionResult(success=True, content=results)
    
    def validate_intent(self, intent: Dict) -> bool:
        return intent.get("category") == "web_search"

# 2. 注册执行器
ExecutorRegistry.register("web_search", WebSearchExecutor)

# 3. 构建时传入依赖
executors = ExecutorRegistry.build_all(search_engine=my_search_engine)
```

### 7.2 执行器依赖注入

```python
# 通过 kwargs 传入依赖
executors = ExecutorRegistry.build_all(
    rag_workflow=rag_workflow,
    agent=agent,
    skill_registry=skill_registry,
    mcp_client=mcp_client,
)
```

---

## 相关文档

- [LangGraph状态图总览](./LangGraph状态图总览.md)
- [意图识别流程](./意图识别流程.md)
- [技能系统流程](./技能系统流程.md)
- [MCP工具调用流程](./MCP工具调用流程.md)