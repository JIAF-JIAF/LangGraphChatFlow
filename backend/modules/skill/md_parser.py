"""
Skill Markdown 解析器
将 .skill.md 文件解析为结构化的技能定义
"""

import re
from typing import Dict, List, Optional, Any


class SkillParser:
    """Markdown 技能文件解析器"""

    @staticmethod
    def parse(file_path: str) -> Optional[Dict[str, Any]]:
        """
        解析技能文件
        
        Args:
            file_path: 技能文件路径
            
        Returns:
            技能定义字典，解析失败返回 None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return SkillParser._parse_content(content)
        except Exception as e:
            print(f"[SKILL] 解析文件失败 {file_path}: {e}")
            return None

    @staticmethod
    def _parse_content(content: str) -> Dict[str, Any]:
        """解析技能文件内容"""
        skill = {
            'name': '',
            'title': '',
            'version': '',
            'author': '',
            'description': '',
            'trigger_keywords': [],
            'difficulty_level': 3,
            'steps': [],
            'tools': [],
            'knowledge': [],
            'output_format': ''
        }

        # 解析基本信息（通过列表项）
        info_pattern = r'- \*\*([^:]+)\*\*:\s*(.+)'
        for match in re.finditer(info_pattern, content):
            key = match.group(1).strip()
            value = match.group(2).strip()
            
            if key == '名称':
                skill['name'] = value
            elif key == '标题':
                skill['title'] = value
            elif key == '版本':
                skill['version'] = value
            elif key == '作者':
                skill['author'] = value

        # 解析技能描述（在"技能描述"标题后）
        desc_match = re.search(r'## 技能描述\n([\s\S]*?)\n## ', content)
        if desc_match:
            skill['description'] = desc_match.group(1).strip()

        # 解析触发关键词
        keyword_section = re.search(r'### 关键词触发\n([\s\S]*?)\n(?:###|##|$)', content)
        if keyword_section:
            keywords = []
            for line in keyword_section.group(1).strip().split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    keywords.append(line[2:].strip())
            skill['trigger_keywords'] = keywords

        # 解析难度等级
        level_match = re.search(r'### 难度等级\n(\d+)', content)
        if level_match:
            skill['difficulty_level'] = int(level_match.group(1))

        # 解析执行流程步骤
        steps_section = re.search(r'## 执行流程\n([\s\S]*?)\n(?:## |$)', content)
        if steps_section:
            steps = []
            step_pattern = r'### 步骤(\d+)[：:]\s*([^\n]+)\n([\s\S]*?)(?=\n### 步骤|$)'
            for match in re.finditer(step_pattern, steps_section.group(1)):
                step_info = {
                    'number': int(match.group(1)),
                    'name': match.group(2).strip(),
                    'details': {}
                }
                # 解析步骤详情
                details_content = match.group(3)
                detail_pattern = r'- \*\*([^:]+)\*\*:\s*(.+)'
                for detail_match in re.finditer(detail_pattern, details_content):
                    detail_key = detail_match.group(1).strip()
                    detail_value = detail_match.group(2).strip()
                    # 解析工具列表
                    if detail_key == '工具' and detail_value.startswith('['):
                        tools = re.findall(r"'([^']+)'|\"([^\"]+)\"", detail_value)
                        step_info['details'][detail_key] = [t[0] or t[1] for t in tools]
                    else:
                        step_info['details'][detail_key] = detail_value
                steps.append(step_info)
            skill['steps'] = steps

        # 解析工具依赖
        tools_section = re.search(r'## 工具依赖\n([\s\S]*?)\n(?:## |$)', content)
        if tools_section:
            tools = []
            # 匹配表格行（简单匹配）
            lines = tools_section.group(1).strip().split('\n')
            header_skipped = False
            for line in lines:
                if not header_skipped:
                    header_skipped = True
                    continue
                # 提取工具名称（第一个竖线后的内容）
                parts = line.split('|')
                if len(parts) >= 2:
                    tool_name = parts[1].strip()
                    if tool_name:
                        tools.append(tool_name)
            skill['tools'] = tools

        # 解析专业知识
        knowledge_section = re.search(r'## 专业知识\n([\s\S]*?)\n(?:## |$)', content)
        if knowledge_section:
            knowledge = []
            for line in knowledge_section.group(1).strip().split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    knowledge.append(line[2:].strip())
            skill['knowledge'] = knowledge

        # 解析输出格式
        format_section = re.search(r'## 输出格式\n```[a-z]*\n([\s\S]*?)```', content)
        if format_section:
            skill['output_format'] = format_section.group(1).strip()

        return skill
