"""
skill_instructions 工具

加载技能完整指令

【功能说明】
加载指定技能的完整指令内容（SKILL.md 中的 instructions 字段）。
这是技能发现的第二步，遵循 Skills as Tools 标准的"加载"阶段。

【调用者】
- LangChain Agent：在 execute_task 节点中，当 Agent 已通过 skill_list 确定要使用的技能后调用
- 调用时机：skill_list 返回技能名称后，Agent 决定使用该技能

【消费者】
- LangChain Agent：获取指令内容后，按照指令步骤执行任务
- 返回格式：Markdown 格式的指令文本，包含 Workflow 步骤、示例、注意事项等

【工作流程】
1. Agent 通过 skill_list 找到目标技能（如 drawio-skill）
2. Agent 调用 skill_instructions(skill_name="drawio-skill")
3. 返回指令内容：
   ```
   ## Workflow
   1. 分析用户需求，确定图表类型
   2. 生成对应的 XML 代码
   3. 使用 skill_save_file 保存文件
   ...
   ```
4. Agent 按照指令步骤执行，可能调用 skill_save_file、skill_run_script 等

【参数说明】
- skill_name: 技能名称（必须）
  - 来源：skill_list 返回的技能名称
  - 示例："drawio-skill"、"report-skill"

【返回值】
- 成功：技能的完整指令内容（Markdown 格式）
- 失败："技能不存在: {skill_name}" 或 "技能 {skill_name} 没有定义指令"

【典型指令内容】
包含以下部分：
- Workflow：执行步骤
- Examples：使用示例
- Notes：注意事项
- References：参考文档链接
"""

from typing import Any
from pydantic import BaseModel, Field, PrivateAttr
from langchain_core.tools import BaseTool
from modules.logger import log
from .factory import SkillToolFactory


class SkillNameInput(BaseModel):
    skill_name: str = Field(description="技能名称")


class SkillInstructionsTool(BaseTool):
    name: str = "skill_instructions"
    description: str = "加载指定技能的完整指令内容。当需要使用某个技能时调用此工具获取详细指令，然后按指令执行。"
    args_schema: type[BaseModel] = SkillNameInput
    
    _loader: Any = PrivateAttr()
    
    def __init__(self, loader: Any, **data):
        super().__init__(**data)
        self._loader = loader
    
    def _run(self, skill_name: str) -> str:
        log(f"skill_instructions 被调用，skill_name={skill_name}", module="Skill.Tools")
        skill = self._loader.load_skill(skill_name)
        
        if not skill:
            return f"技能不存在: {skill_name}"
        
        instructions = skill.get("instructions", "")
        
        if not instructions:
            return f"技能 {skill_name} 没有定义指令"
        
        return instructions


def build_skill_instructions_tool(loader, matcher, executor):
    """
    构建 skill_instructions 工具
    
    Args:
        loader: 技能加载器
        matcher: 技能匹配器
        executor: 技能执行器
        
    Returns:
        skill_instructions 工具实例
    """
    return SkillInstructionsTool(loader=loader)


SkillToolFactory.register("skill_instructions", build_skill_instructions_tool)
