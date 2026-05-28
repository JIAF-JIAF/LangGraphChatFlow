# MCP工具调用流程

> 文档版本：v1.0  
> 更新时间：2026-05-28  
> 核心模块：`server/mcp_module/`

---

## 目录

- [一、流程概述](#一流程概述)
- [二、完整流程图](#二完整流程图)
- [三、MCP架构设计](#三mcp架构设计)
- [四、工具注册机制](#四工具注册机制)
- [五、工具调用流程](#五工具调用流程)
- [六、现有工具列表](#六现有工具列表)
- [七、扩展指南](#七扩展指南)

---

## 一、流程概述

MCP（Model Context Protocol）工具系统支持调用外部工具服务：

| 步骤 | 功能 | 模块 |
|------|------|------|
| **意图识别** | 识别为 MCP 类别意图 | `IntentRouter` |
| **工具选择** | 选择对应工具 | `McpExecutor` |
| **请求构建** | 构建 MCP 请求 | `McpClient` |
| **工具调用** | 调用 MCP 服务 | `McpServer` |
| **结果解析** | 解析工具响应 | `McpExecutor` |

---

## 二、完整流程图

```mermaid
flowchart TB
    subgraph Phase1["阶段1: 意图识别"]
        A[用户查询] --> B[IntentRouter.route]
        B --> C[识别为 MCP 类别]
        C --> D[Intent: category=MCP]
    end
    
    subgraph Phase2["阶段2: 工具选择"]
        D --> E[McpExecutor]
        E --> F[提取 target 工具名]
        F --> G[查找工具定义]
        G --> H[获取工具 schema]
    end
    
    subgraph Phase3["阶段3: 请求构建"]
        H --> I[McpClient]
        I --> J[构建请求参数]
        J --> K[验证参数格式]
        K --> L[生成 MCP 请求]
    end
    
    subgraph Phase4["阶段4: 工具调用"]
        L --> M[McpServer]
        M --> N[接收请求]
        N --> O[执行工具逻辑]
        O --> P[生成响应]
    end
    
    subgraph Phase5["阶段5: 结果解析"]
        P --> Q[McpExecutor]
        Q --> R[解析响应格式]
        R --> S[提取工具结果]
        S --> T[格式化为 ExecutionResult]
    end
    
    subgraph Phase6["阶段6: 结果返回"]
        T --> U[存入 intent_results]
        U --> V[CallModelNode]
        V --> W[生成最终回答]
    end
    
    style A fill:#e1f5fe,color:#01579b
    style D fill:#c8e6c9,color:#1a5e20
    style L fill:#fff3e0,color:#e65100
    style P fill:#f3e5f5,color:#7b1fa2
    style W fill:#bbdefb,color:#0d47a1
```

---

## 三、MCP架构设计

### 3.1 MCP服务架构

```mermaid
flowchart TB
    subgraph MCP["MCP 服务架构"]
        A[LangGraph Agent] --> B[McpExecutor]
        B --> C[McpClient]
        C --> D[McpServer<br/>独立部署]
        D --> E[Tool Registry]
        E --> F[Tool 1]
        E --> G[Tool 2]
        E --> H[Tool 3]
    end
    
    style MCP fill:#e1f5fe,color:#01579b
```

### 3.2 MCP协议结构

```python
# MCP请求
McpRequest(
    tool_name="web_search",
    parameters={
        "query": "人工智能最新进展",
        "limit": 5,
    },
)

# MCP响应
McpResponse(
    success=True,
    result={
        "results": [
            {"title": "...", "url": "...", "summary": "..."},
        ],
    },
)
```

---

## 四、工具注册机制

### 4.1 工具定义结构

```python
ToolDefinition(
    name="web_search",
    description="网络搜索工具",
    parameters={
        "query": {"type": "string", "required": True},
        "limit": {"type": "integer", "default": 5},
    },
    returns={
        "results": {"type": "array"},
    },
)
```

### 4.2 工具注册流程

```mermaid
flowchart LR
    subgraph Register["工具注册流程"]
        A[ToolDefinition] --> B[ToolRegistry]
        B --> C[验证定义]
        C --> D[存储到注册表]
        D --> E[暴露给 McpServer]
    end
    
    style Register fill:#c8e6c9,color:#1a5e20
```

---

## 五、工具调用流程

### 5.1 参数验证流程

```mermaid
flowchart TB
    subgraph Validate["参数验证"]
        A[请求参数] --> B[获取 schema]
        B --> C{参数类型匹配?}
        C -->|匹配| D{必填参数存在?}
        C -->|不匹配| E[返回类型错误]
        D -->|存在| F[参数验证通过]
        D -->|不存在| G[返回缺失错误]
    end
    
    style Validate fill:#fff3e0,color:#e65100
```

### 5.2 工具执行流程

```mermaid
flowchart TB
    subgraph Execute["工具执行"]
        A[验证通过的请求] --> B[调用工具函数]
        B --> C[执行工具逻辑]
        C --> D{执行成功?}
        D -->|成功| E[生成结果]
        D -->|失败| F[捕获异常]
        F --> G[返回错误信息]
        E --> H[格式化响应]
    end
    
    style Execute fill:#f3e5f5,color:#7b1fa2
```

---

## 六、现有工具列表

| 工具名称 | 功能 | 参数 |
|----------|------|------|
| **web_search** | 网络搜索 | query, limit |
| **file_read** | 文件读取 | path |
| **file_write** | 文件写入 | path, content |
| **database_query** | 数据库查询 | sql |

---

## 七、扩展指南

### 7.1 新增MCP工具

```python
# 1. 定义工具
@tool_registry.register
def my_tool(param1: str, param2: int) -> dict:
    """
    我的自定义工具
    
    Args:
        param1: 参数1描述
        param2: 参数2描述
    
    Returns:
        执行结果
    """
    # 执行逻辑
    return {"result": "执行结果"}

# 2. 工具会自动注册到 McpServer
# 3. LangGraph Agent 可通过 Intent 调用
```

### 7.2 MCP服务部署

```yaml
# mcp_server.yaml
server:
  host: 0.0.0.0
  port: 8080
  
tools:
  - name: web_search
    module: tools.web_search
  - name: file_read
    module: tools.file_ops
```

---

## 相关文档

- [LangGraph状态图总览](./LangGraph状态图总览.md)
- [Direct模式流程](./Direct模式流程.md)
- [意图识别流程](./意图识别流程.md)