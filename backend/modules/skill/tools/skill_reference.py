"""
skill_reference 工具

读取技能参考文档

【功能说明】
读取技能目录下的参考文档（如 API 文档、模板说明、配置指南等）。
这是技能发现的第三步，遵循 Skills as Tools 标准的"资源获取"阶段。

【调用者】
- LangChain Agent：在 execute_task 节点中，当 Agent 执行指令时需要参考额外文档时调用
- 调用时机：skill_instructions 返回的指令中包含 References 部分，或执行过程中需要查阅文档

【消费者】
- LangChain Agent：获取参考文档内容后，用于辅助生成正确的内容
- 返回格式：文档的原始内容（通常是 Markdown 或文本格式）

【工作流程】
1. Agent 通过 skill_instructions 获取指令，指令中提到："参考 references/drawio-api.md 了解 XML 格式"
2. Agent 调用 skill_reference(skill_name="drawio-skill", reference_path="references/drawio-api.md")
3. 返回文档内容：
   ```
   # DrawIO XML API
   
   ## 节点定义
   <mxCell id="..." value="..." style="..." />
   ...
   ```
4. Agent 根据文档内容生成符合规范的输出

【参数说明】
- skill_name: 技能名称（必须）
  - 来源：当前正在使用的技能名称
- reference_path: 参考文档路径（必须）
  - 相对于技能目录下的 references/ 目录
  - 示例："references/api.md"、"references/template.md"

【返回值】
- 成功：参考文档的完整内容
- 失败："参考文档不存在: {skill_name}/{reference_path}"

【典型参考文档】
- API 文档：第三方服务的 API 说明
- 模板文档：输出格式的模板和规范
- 配置文档：配置项说明和示例
- 示例文档：完整的示例代码或输出
"""

from typing import Any
from pydantic import BaseModel, Field, PrivateAttr
from langchain_core.tools import BaseTool
from modules.logger import log
from .factory import SkillToolFactory


class SkillReferenceInput(BaseModel):
    skill_name: str = Field(description="技能名称")
    reference_path: str = Field(description="参考文档路径，如 references/api.md")


class SkillReferenceTool(BaseTool):
    name: str = "skill_reference"
    description: str = "读取技能的参考文档。当技能指令中引用了额外文档时调用此工具获取。"
    args_schema: type[BaseModel] = SkillReferenceInput
    
    _loader: Any = PrivateAttr()
    
    def __init__(self, loader: Any, **data):
        super().__init__(**data)
        self._loader = loader
    
    def _run(self, skill_name: str, reference_path: str) -> str:
        log(f"skill_reference 被调用，skill_name={skill_name}, path={reference_path}", module="Skill.Tools")
        content = self._loader.get_reference(skill_name, reference_path)
        
        if content is None:
            return f"参考文档不存在: {skill_name}/{reference_path}"
        
        return content


def build_skill_reference_tool(loader, matcher, executor):
    """
    构建 skill_reference 工具
    
    Args:
        loader: 技能加载器
        matcher: 技能匹配器
        executor: 技能执行器
        
    Returns:
        skill_reference 工具实例
    """
    return SkillReferenceTool(loader=loader)


SkillToolFactory.register("skill_reference", build_skill_reference_tool)
