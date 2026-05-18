"""
Skill 管理器
负责加载、匹配和执行技能
"""

import os
import glob
from typing import Dict, List, Optional, Any
from .md_parser import SkillParser


class SkillManager:
    """技能管理器"""

    def __init__(self, skills_dir: str = "skills"):
        """
        初始化技能管理器
        
        Args:
            skills_dir: 技能文件目录（相对于 backend 目录）
        """
        self.skills_dir = skills_dir
        self.skills: Dict[str, Dict[str, Any]] = {}
        self._load_skills()

    def _load_skills(self):
        """加载所有技能文件"""
        # 构建完整路径
        # __file__ 是 modules/skill/skill_manager.py
        # 需要向上三层目录到达 backend 目录
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        full_path = os.path.join(backend_dir, self.skills_dir)
        
        if not os.path.exists(full_path):
            print(f"[SKILL] 技能目录不存在: {full_path}")
            return

        # 只加载 .skill.md 文件，排除其他文件
        pattern = os.path.join(full_path, "*.skill.md")
        skill_files = glob.glob(pattern)
        
        print(f"[SKILL] 发现 {len(skill_files)} 个技能文件")
        
        for file_path in skill_files:
            # 排除规范文档
            if "SKILL_SPEC" in file_path:
                continue
                
            skill = SkillParser.parse(file_path)
            if skill and skill.get('name'):
                self.skills[skill['name']] = skill
                print(f"[SKILL] 加载技能: {skill['name']} - {skill['title']}")

    def get_all_skills(self) -> List[Dict[str, Any]]:
        """获取所有技能列表"""
        return list(self.skills.values())

    def get_skill(self, name: str) -> Optional[Dict[str, Any]]:
        """获取指定技能"""
        return self.skills.get(name)

    def match_skill(self, query: str) -> Optional[Dict[str, Any]]:
        """
        根据用户查询匹配最合适的技能
        
        Args:
            query: 用户查询
            
        Returns:
            匹配到的技能，未匹配返回 None
        """
        matched_skills = []
        
        for skill_name, skill in self.skills.items():
            keywords = skill.get('trigger_keywords', [])
            # 检查是否有任何关键词匹配
            if any(keyword in query for keyword in keywords):
                matched_skills.append((skill, len([k for k in keywords if k in query])))
        
        if not matched_skills:
            return None
        
        # 返回匹配关键词最多的技能
        matched_skills.sort(key=lambda x: x[1], reverse=True)
        return matched_skills[0][0]

    def generate_skill_prompt(self, skill: Dict[str, Any], query: str) -> str:
        """
        生成技能专属的 prompt
        
        Args:
            skill: 技能定义
            query: 用户查询
            
        Returns:
            构建好的 prompt
        """
        # 构建步骤描述
        steps_desc = ""
        for step in skill.get('steps', []):
            steps_desc += f"{step['number']}. {step['name']}\n"
            for key, value in step.get('details', {}).items():
                if isinstance(value, list):
                    value = ", ".join(value)
                steps_desc += f"   - {key}: {value}\n"
        
        # 构建工具列表
        tools_list = ", ".join(skill.get('tools', []))
        
        # 构建专业知识
        knowledge_desc = "\n".join(f"- {k}" for k in skill.get('knowledge', []))
        
        prompt = f"""你现在扮演【{skill['title']}】角色。
        
技能描述：{skill['description']}

执行步骤：
{steps_desc}

可用工具：{tools_list}

专业知识：
{knowledge_desc}

用户请求：{query}

请按照上述步骤执行，必要时调用工具，并输出最终结果。"""
        
        return prompt

    def reload_skills(self):
        """重新加载所有技能"""
        self.skills.clear()
        self._load_skills()
