"""
基于技能的任务生成器
"""

from typing import List, Dict, Any, Optional
from ..state import AgentState
from .base import TaskGeneratorHandler


class SkillTaskGenerator(TaskGeneratorHandler):
    """基于技能的任务生成器"""
    
    def _try_handle(self, state: AgentState, planner, query: str) -> Optional[List[Dict[str, Any]]]:
        matched_skill = state.get("matched_skill")
        if not matched_skill:
            return None
        
        print(f"[任务生成] 使用技能: {matched_skill['name']} - {matched_skill['title']}")
        
        steps = matched_skill.get("steps", [])
        subtasks = []
        
        for i, step in enumerate(steps):
            task_description = f"步骤{i+1}: {step['name']}\n"
            task_description += f"目标: {step['details'].get('目标', '')}\n"
            task_description += f"操作: {step['details'].get('操作', '')}\n"
            task_description += f"输入: {step['details'].get('输入', query)}"
            
            subtasks.append({
                "task_id": f"task_{i+1}",
                "task_description": task_description.strip(),
                "dependencies": [f"task_{i}" if i > 0 else ""],
                "status": "pending",
                "result": "",
                "skill_name": matched_skill['name']
            })
        
        return subtasks
