# 技能系统文档

基于 `pydantic-ai-skills` 的技能匹配和执行引擎，提供专业领域的深度服务。

## 技术架构

技能系统采用分层架构设计，使用业界成熟方案：

| 层级 | 组件 | 技术方案 | 职责 |
|------|------|---------|------|
| 加载层 | `SkillLoader` | `pydantic-ai-skills.SkillsToolset` | 技能发现和加载 |
| 匹配层 | `SkillMatcher` | 关键词匹配 | 技能路由选择 |
| 执行层 | `SkillExecutor` | `subprocess` | 脚本安全执行 |
| 工具层 | `SkillTools` | `LangChain Tools` | Agent 工具封装 |
| 管理层 | `SkillManager` | - | 生命周期管理 |
| 安装层 | `SkillInstaller` | `pydantic-ai-skills` + GitHub API | 技能安装/卸载 |

## 技能工具列表

Agent 通过以下工具与技能系统交互：

| 工具名称 | 功能描述 | 调用时机 |
|---------|---------|---------|
| `skill_list` | 列出/搜索可用技能 | 发现技能阶段 |
| `skill_instructions` | 加载技能完整指令 | 确定使用技能后 |
| `skill_reference` | 读取技能参考文档 | 需要额外文档时 |
| `skill_save_file` | 保存生成内容到文件 | 生成 XML/JSON 等内容时 |
| `skill_run_script` | 执行技能脚本 | 需要运行脚本时 |

## 内置技能

| 技能名称 | 功能描述 | 触发关键词 |
|---------|---------|-----------|
| data-analysis | 数据分析、生成可视化报告 | 分析、报告、数据、统计、趋势 |
| drawio-skill | 绘制流程图、架构图 | 画图、流程图、架构图、设计 |
| tldraw-skill | 协作绘图、白板 | 白板、绘图、协作 |
| trip-plan | 旅行规划、行程安排 | 旅行、旅游、行程、攻略 |

## 技能执行流程图

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              SKILL 执行流程                                          │
└─────────────────────────────────────────────────────────────────────────────────────┘

用户请求: "帮我画一个流程图"
        │
        ▼
┌───────────────────┐
│  1. skill_list    │  ← Agent 调用，搜索相关技能
│  query="画图 流程图"│
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  SkillMatcher     │  ← 关键词匹配
│  匹配: drawio-skill│
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│2. skill_instructions│ ← 加载技能指令
│  skill_name=drawio │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  SKILL.md 内容    │  ← 返回完整指令
│  - Workflow       │
│  - Step 0-7       │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│3. skill_reference │  ← 按需加载参考文档
│  diagram-types.md │
└─────────┬─────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    4. 执行 Workflow                            │
│                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│  │ Step 1      │───▶│ Step 2      │───▶│ Step 3      │───▶ ...  │
│  │ Check deps  │    │ Plan        │    │ Generate    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘            │
│         │                  │                  │                │
│         ▼                  ▼                  ▼                │
│  检查 draw.io CLI    规划形状/布局      生成 .drawio XML          │
│                                            │                   │
│                                            ▼                   │
│                                   ┌───────────────────┐          │
│                                   │ 5. skill_save_file│        │
│                                   │  保存 XML 到文件   │         │
│                                   └─────────┬─────────┘          │
│                                             │                  │
│                                             ▼                  │
│                                   ┌───────────────────┐          │
│                                   │ 6. skill_run_script│       │
│                                   │  export to PNG    │        │
│                                   └─────────┬─────────┘          │
└─────────────────────────────────────────────┼────────────────────────┘
                                              │
                                              ▼
┌───────────────────────────────────────────────────────────────────┐
│                         7. 返回结果                           │
│                                                              │
│  "流程图已生成：login_flow.drawio                              │
│   预览图：login_flow.drawio.png                               │
│   您可以用 draw.io 打开编辑"                                   │
└───────────────────────────────────────────────────────────────────┘
```

## 技能安装流程

```
GitHub URL → SkillInstaller.install_from_url()
                    │
                    ├── 1. 解析 GitHub URL
                    │      提取: user, repo, branch, path
                    │
                    ├── 2. 下载 ZIP 包
                    │      API: /repos/{user}/{repo}/zipball/{branch}
                    │
                    ├── 3. 解压到 skills/{skill_name}/
                    │
                    ├── 4. SkillsToolset.reload()
                    │      重新扫描技能目录
                    │
                    └── 5. 返回安装结果
```

### 安装示例

```python
from api.skill_installer import get_installer

installer = get_installer()

# 从 GitHub 安装
result = installer.install_from_url("https://github.com/Agents365-ai/drawio-skill")
print(result.message)  # 技能 drawio-skill 安装成功

# 列出已安装技能
skills = installer.list_installed()
print(skills)  # ['data-analysis', 'drawio-skill', 'tldraw-skill']

# 获取技能信息
info = installer.get_skill_info("drawio-skill")
print(info['description'])

# 卸载技能
installer.uninstall("drawio-skill")
```

## 技能目录结构

```
skills/
├── data-analysis/            # 数据分析技能
│   └── SKILL.md
├── drawio-skill/             # 流程图绘制技能
│   ├── SKILL.md              # 技能定义（必需）
│   ├── references/           # 参考文档
│   │   ├── diagram-types.md
│   │   ├── style-extraction.md
│   │   ├── style-presets.md
│   │   └── troubleshooting.md
│   ├── scripts/              # 可执行脚本
│   │   ├── encode_drawio_url.py
│   │   └── repair_png.py
│   ├── styles/               # 样式配置
│   │   ├── built-in/
│   │   │   ├── corporate.json
│   │   │   ├── default.json
│   │   │   └── handdrawn.json
│   │   └── schema.json
│   └── output/               # 输出目录（自动创建）
├── tldraw-skill/             # 白板协作技能
│   └── SKILL.md
└── trip-plan/                # 旅行规划技能
    └── SKILL.md
```

## SKILL.md 格式

```yaml
---
name: drawio-skill
version: 1.5.2
description: Use when the user requests diagrams, flowcharts...
license: MIT
homepage: https://github.com/Agents365-ai/drawio-skill
metadata:
  author: Agents365-ai
  version: 1.5.2
---

# Draw.io Diagrams

## Overview
Generate .drawio XML files...

## Workflow
Step 1: Check deps
Step 2: Plan
Step 3: Generate
...
```

### 元数据字段说明

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | 是 | 技能唯一标识，用于匹配和调用 |
| `version` | 是 | 版本号，遵循语义化版本 |
| `description` | 是 | 技能描述，用于 `skill_list` 展示 |
| `license` | 否 | 开源协议 |
| `homepage` | 否 | 项目主页 |
| `metadata` | 否 | 扩展元数据（author、tags 等） |

## 开发自定义技能

### 1. 创建技能目录

```bash
mkdir -p skills/my-skill
```

### 2. 编写 SKILL.md

```yaml
---
name: my-skill
version: 1.0.0
description: 我的自定义技能
---

# My Skill

## Overview
技能功能说明...

## Workflow
Step 1: xxx
Step 2: xxx
```

### 3. 添加脚本（可选）

```bash
mkdir -p skills/my-skill/scripts
# 创建 scripts/process.py
```

### 4. 添加参考文档（可选）

```bash
mkdir -p skills/my-skill/references
# 创建 references/api.md
```

## API 接口

### 安装技能

```http
POST /api/skills/install
Content-Type: application/json

{
  "url": "https://github.com/user/skill-repo"
}
```

### 列出技能

```http
GET /api/skills/list
```

响应：
```json
{
  "skills": [
    {
      "name": "drawio-skill",
      "description": "绘制流程图、架构图",
      "version": "1.5.2",
      "path": "/path/to/skills/drawio-skill"
    }
  ]
}
```

### 卸载技能

```http
DELETE /api/skills/{skill_name}
```

## 依赖

```txt
# requirements.txt
pydantic-ai-skills>=0.10.0
pyyaml>=6.0
requests>=2.31.0
```
