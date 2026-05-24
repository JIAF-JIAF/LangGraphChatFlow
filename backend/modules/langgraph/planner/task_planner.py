"""
任务规划器模块

负责将复杂用户需求拆分为有序的子任务队列，支持多步骤推理。

核心功能：
1. 分析用户查询的复杂度
2. 拆分任务为有序子任务
3. 管理任务依赖关系
"""

import json
import os
from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage

from modules.logger import log, exception


class TaskPlanner:
    """
    任务规划器：将复杂问题拆分为可执行的子任务序列
    
    使用 LLM 进行任务分解，支持：
    - 简单问题直接回答
    - 复杂问题拆分为多个子任务
    - 任务依赖关系管理

    配置项（环境变量）：
        TASK_PLANNER_MAX_TASKS: 最大子任务数量（默认5）
        TASK_PLANNER_MIN_TASKS: 最小子任务数量（默认1）
        TASK_PLANNER_ENABLE: 是否启用规划（默认True）
    """

    def __init__(self, llm_client=None):
        """
        初始化任务规划器
        
        Args:
            llm_client: LLM 客户端实例
        """
        self.llm_client = llm_client
        
        self.max_tasks = int(os.getenv("TASK_PLANNER_MAX_TASKS", 5))
        self.min_tasks = int(os.getenv("TASK_PLANNER_MIN_TASKS", 1))
        self.enable_planning = os.getenv("TASK_PLANNER_ENABLE", "true").lower() in ("true", "1", "yes", "on")

    def _is_simple_question(self, query: str) -> bool:
        """
        使用 LLM 判断是否为简单问题（不需要规划）
        
        Args:
            query: 用户查询
            
        Returns:
            True - 简单问题，直接回答
            False - 复杂问题，需要规划
        """
        if not self.enable_planning:
            return True
        
        if not self.llm_client:
            return True
            
        return self._llm_judge_complexity(query)

    def _llm_judge_complexity(self, query: str) -> bool:
        """
        使用 LLM 判断问题复杂度（兼容旧接口）
        
        Args:
            query: 用户查询
            
        Returns:
            True - 简单问题
            False - 复杂问题
        """
        level = self._llm_evaluate_difficulty(query)
        return level <= 2  # 1-2级为简单问题
    
    def _llm_evaluate_difficulty(self, query: str) -> int:
        """
        使用 LLM 评估问题难度等级（1-5级）
        
        Args:
            query: 用户查询
            
        Returns:
            难度等级 1-5
        """
        prompt = f"""请评估以下问题的难度，分为1-5级：
            1级：简单事实查询（如"什么是人工智能"、"谁发明了电话"）
            2级：需要简单推理（如"为什么天空是蓝色的"、"如何煮米饭"）
            3级：需要多步骤分析（如"如何制定旅行计划"、"分析市场趋势"）
            4级：需要综合多领域知识（如"如何设计一个电商系统"、"分析政策影响"）
            5级：需要创造性解决方案（如"如何提高产品销量"、"制定营销策略"）

问题：{query}

请只回答数字。"""

        try:
            response = self.llm_client.chat.invoke([HumanMessage(content=prompt)])
            result = response.content.strip()
            level = int(result) if result.isdigit() else 3
            log(f"LLM 难度评估: {query[:30]}... -> 难度等级 {level}", "Planner")
            return max(1, min(5, level))  # 确保在1-5范围内
        except Exception as e:
            exception(f"难度评估失败，默认等级3: {e}", "Planner", e)
            return 3

    def plan(self, query: str, context: str = "") -> List[Dict[str, Any]]:
        """
        将复杂查询拆分为子任务
        
        Args:
            query: 用户原始查询
            context: 检索到的上下文（可选）
        
        Returns:
            子任务列表，每个任务包含：
                - task_id: 任务唯一标识
                - task_description: 任务描述
                - dependencies: 依赖的前置任务ID列表
                - status: 任务状态（pending/completed/failed）
                - result: 任务执行结果
        """
        if not self.llm_client:
            # 无LLM时使用简单策略
            return [{
                "task_id": "task_1",
                "task_description": query,
                "dependencies": [],
                "status": "pending",
                "result": ""
            }]

        # 使用难度评估决定任务数
        difficulty_level = self._llm_evaluate_difficulty(query)
        
        # 难度等级 -> 建议任务数
        task_count_map = {
            1: 1,  # 简单事实查询
            2: 1,  # 简单推理
            3: 2,  # 多步骤分析
            4: 3,  # 综合多领域知识
            5: 4   # 创造性解决方案
        }
        
        target_task_count = task_count_map.get(difficulty_level, 2)
        
        # 1-2级简单问题，直接返回单任务
        if difficulty_level <= 2:
            return [{
                "task_id": "task_1",
                "task_description": query,
                "dependencies": [],
                "status": "pending",
                "result": ""
            }]

        # 复杂问题，调用LLM生成规划
        subtasks = self._generate_plan_with_llm(query, context, target_task_count)
        
        # 如果返回空数组，说明信息不足无法规划，直接返回单任务让 Agent 处理
        if not subtasks:
            log("信息不足无法规划，直接返回单任务", "Planner")
            return [{
                "task_id": "task_1",
                "task_description": query,
                "dependencies": [],
                "status": "pending",
                "result": ""
            }]
        
        return subtasks

    def _generate_plan_with_llm(self, query: str, context: str = "", target_task_count: int = 2) -> List[Dict[str, Any]]:
        """
        使用 LLM 生成任务规划
        
        Args:
            query: 用户查询
            context: 参考上下文
            target_task_count: 目标任务数量（基于难度评估）
        
        Returns:
            结构化的子任务列表
        """
        prompt = f"""
        你是一个专业的任务规划专家。请将用户的复杂需求拆分成多个有序的子任务。

        用户查询：{query}

        参考上下文（如果有）：
        {context[:800] if context else '无'}

        请按照以下格式输出JSON：
        [
            {{
                "task_id": "task_1",
                "task_description": "第一步需要执行的具体任务",
                "dependencies": []
            }},
            {{
                "task_id": "task_2",
                "task_description": "第二步需要执行的具体任务",
                "dependencies": ["task_1"]
            }}
        ]

        重要约束：
        1. 子任务数量控制在 {target_task_count} 个左右（{target_task_count-1}~{target_task_count+1}个）
        2. 任务之间要有清晰的逻辑顺序和依赖关系
        3. 每个任务要具体、可执行
        4. 避免重复的任务描述
        5. 最后一个任务应该是总结或给出最终答案
        6. 如果问题需要向用户追问信息才能回答，说明信息不足，不要拆分任务，直接返回空数组 []
        7. 一旦决定拆分任务，每个子任务必须独立完成计划内容，不得追问用户
        """

        try:
            response = self.llm_client.chat.invoke([HumanMessage(content=prompt)])
            subtasks = json.loads(response.content)
            
            # 验证并补全任务结构
            return self._validate_and_normalize_tasks(subtasks)
            
        except json.JSONDecodeError as e:
            exception(f"JSON解析失败: {e}", "Planner", e)
            return self._create_fallback_plan(query)
        except Exception as e:
            exception(f"规划生成失败: {e}", "Planner", e)
            return self._create_fallback_plan(query)

    def _validate_and_normalize_tasks(self, subtasks: List[Dict]) -> List[Dict[str, Any]]:
        """
        验证并标准化任务列表格式
        
        Args:
            subtasks: 原始任务列表
            
        Returns:
            标准化后的任务列表
        """
        normalized = []
        
        for i, task in enumerate(subtasks[:self.max_tasks], 1):
            task_id = task.get("task_id", f"task_{i}")
            description = task.get("task_description", "")
            dependencies = task.get("dependencies", [])
            
            # 确保依赖是字符串列表
            if not isinstance(dependencies, list):
                dependencies = []
            
            normalized.append({
                "task_id": task_id,
                "task_description": description.strip(),
                "dependencies": dependencies,
                "status": "pending",
                "result": ""
            })
        
        return normalized

    def _create_fallback_plan(self, query: str) -> List[Dict[str, Any]]:
        """
        创建降级方案：将查询作为单个任务
        
        Args:
            query: 用户查询
            
        Returns:
            单任务列表
        """
        return [{
            "task_id": "task_1",
            "task_description": query,
            "dependencies": [],
            "status": "pending",
            "result": ""
        }]

    def get_next_task(self, subtasks: List[Dict]) -> Optional[int]:
        """
        获取下一个可执行的任务索引
        
        Args:
            subtasks: 任务列表
            
        Returns:
            下一个可执行任务的索引，None表示所有任务已完成
        """
        for idx, task in enumerate(subtasks):
            if task["status"] == "pending":
                # 检查依赖是否都已完成
                deps_completed = all(
                    any(t["task_id"] == dep and t["status"] == "completed" for t in subtasks)
                    for dep in task["dependencies"]
                )
                if deps_completed:
                    return idx
        return None

    def update_task_result(self, subtasks: List[Dict], task_idx: int, result: str, status: str = "completed") -> List[Dict]:
        """
        更新任务执行结果
        
        Args:
            subtasks: 任务列表
            task_idx: 任务索引
            result: 任务执行结果
            status: 任务状态
            
        Returns:
            更新后的任务列表
        """
        if 0 <= task_idx < len(subtasks):
            subtasks[task_idx]["result"] = result
            subtasks[task_idx]["status"] = status
        return subtasks

    def is_all_completed(self, subtasks: List[Dict]) -> bool:
        """
        检查所有任务是否已完成
        
        Args:
            subtasks: 任务列表
            
        Returns:
            True - 所有任务已完成
            False - 还有未完成的任务
        """
        return all(task["status"] in ["completed", "failed"] for task in subtasks)

    def get_summary(self, subtasks: List[Dict]) -> str:
        """
        汇总所有任务结果
        
        Args:
            subtasks: 任务列表
            
        Returns:
            汇总结果字符串
        """
        completed_tasks = [t for t in subtasks if t["status"] == "completed"]
        if not completed_tasks:
            return ""
        
        # 如果只有一个任务，直接返回结果
        if len(completed_tasks) == 1:
            return completed_tasks[0]["result"]
        
        # 多个任务时生成汇总
        summary_parts = []
        for task in completed_tasks:
            if task["result"]:
                summary_parts.append(f"{task['task_description']}: {task['result']}")
        
        return "\n\n".join(summary_parts)
