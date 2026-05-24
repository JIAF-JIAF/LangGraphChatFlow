"""
反思校验器模块

负责对回答进行质量评估，检测幻觉并提供改进建议。

核心功能：
1. 事实一致性校验
2. 回答完整性评估
3. 逻辑合理性检查
4. 提供具体改进建议
"""

import json
import os
from typing import Dict, Any, Optional, List
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document

from modules.logger import log, exception


class ReflectionChecker:
    """
    反思校验器：评估回答质量并提供改进建议
    
    使用 LLM 进行深度反思，支持：
    - 事实准确性校验
    - 完整性评估
    - 逻辑一致性检查
    - 自动生成改进建议

    配置项（环境变量）：
        REFLECTION_CONFIDENCE_THRESHOLD: 通过阈值（默认0.7）
        REFLECTION_ENABLE: 是否启用校验（默认True）
        REFLECTION_MAX_SUGGESTIONS: 最大改进建议数量（默认3）
    """

    def __init__(self, llm_client=None):
        """
        初始化反思校验器
        
        Args:
            llm_client: LLM 客户端实例
        """
        self.llm_client = llm_client
        
        self.confidence_threshold = float(os.getenv("REFLECTION_CONFIDENCE_THRESHOLD", 0.7))
        self.enable_checking = os.getenv("REFLECTION_ENABLE", "true").lower() in ("true", "1", "yes", "on")
        self.max_suggestions = int(os.getenv("REFLECTION_MAX_SUGGESTIONS", 3))

    def reflect(self, query: str, answer: str, documents: Optional[List[Document]] = None) -> Dict[str, Any]:
        """
        对回答进行反思校验
        
        Args:
            query: 用户原始问题
            answer: 当前回答
            documents: 参考文档列表（可选）
            
        Returns:
            校验结果字典：
                - is_passed: 是否通过校验
                - confidence: 置信度 (0-1)
                - feedback: 评估反馈
                - suggestions: 改进建议列表
                - error_type: 错误类型（如果未通过）
        """
        if not self.enable_checking:
            return {
                "is_passed": True,
                "confidence": 1.0,
                "feedback": "校验已跳过",
                "suggestions": [],
                "error_type": None
            }

        if not answer or not answer.strip():
            return {
                "is_passed": False,
                "confidence": 0.0,
                "feedback": "回答为空",
                "suggestions": ["请提供具体的回答内容"],
                "error_type": "empty_answer"
            }

        if self._is_simple_query(query):
            return self._relaxed_check(query, answer)

        if not self.llm_client:
            return self._simple_check(query, answer)

        return self._deep_reflect(query, answer, documents)

    def _is_simple_query(self, query: str) -> bool:
        """
        判断是否为简单问题
        
        Args:
            query: 用户问题
            
        Returns:
            True - 简单问题
        """
        simple_patterns = [
            "是什么", "什么是", "谁能", "哪个", "多少", "什么时候",
            "简单说", "简要", "一句话", "总结", "概述",
            "功能", "能力", "做什么", "能干", "可以帮", "帮我做",
            "介绍一下", "说下", "讲讲", "有哪些",
            "？", "?"
        ]
        query_lower = query.lower()
        return any(pattern in query_lower for pattern in simple_patterns) or len(query) < 15

    def _relaxed_check(self, query: str, answer: str) -> Dict[str, Any]:
        """
        对简单问题使用宽松校验
        
        Args:
            query: 用户问题
            answer: 当前回答
            
        Returns:
            宽松校验结果
        """
        if len(answer) < 10:
            return {
                "is_passed": False,
                "confidence": 0.5,
                "feedback": "回答过于简短",
                "suggestions": ["请提供更完整的回答"],
                "error_type": "too_short"
            }
        return {
            "is_passed": True,
            "confidence": 0.9,
            "feedback": "简单问题，使用宽松标准校验通过",
            "suggestions": [],
            "error_type": None
        }

    def _simple_check(self, query: str, answer: str) -> Dict[str, Any]:
        """
        简单规则校验（无LLM时使用）
        
        Args:
            query: 用户问题
            answer: 当前回答
            
        Returns:
            校验结果
        """
        query_lower = query.lower()
        answer_lower = answer.lower()
        
        # 检查是否直接拒绝回答
        rejection_phrases = ["不知道", "不清楚", "无法回答", "无可奉告", "不了解"]
        if any(phrase in answer_lower for phrase in rejection_phrases):
            return {
                "is_passed": False,
                "confidence": 0.3,
                "feedback": "回答过于简略或拒绝回答",
                "suggestions": ["请尝试提供更详细的回答"],
                "error_type": "rejection"
            }
        
        # 检查回答长度
        if len(answer) < 10:
            return {
                "is_passed": False,
                "confidence": 0.4,
                "feedback": "回答过于简短",
                "suggestions": ["请提供更详细的回答"],
                "error_type": "too_short"
            }
        
        return {
            "is_passed": True,
            "confidence": 0.75,
            "feedback": "通过简单校验",
            "suggestions": [],
            "error_type": None
        }

    def _deep_reflect(self, query: str, answer: str, documents: Optional[List[Document]] = None) -> Dict[str, Any]:
        """
        使用LLM进行深度反思校验
        
        Args:
            query: 用户问题
            answer: 当前回答
            documents: 参考文档
            
        Returns:
            详细的校验结果
        """
        context = "\n\n".join([doc.page_content for doc in documents]) if documents else ""
        
        prompt = f"""
        你是一个严格的质量检验专家。请仔细评估以下回答是否满足用户需求。

        用户问题：{query}

        当前回答：{answer}

        参考文档（如果有）：
        {context[:1200] if context else '无'}

        请按照以下标准进行评估：
        
        评估维度：
        1. 准确性：回答是否基于事实或参考文档？有无虚假信息？
        2. 完整性：是否覆盖了问题的所有关键方面？有无遗漏重要信息？
        3. 逻辑性：推理过程是否合理？结论是否有依据？
        4. 相关性：回答是否直接针对用户问题？有无偏离主题？
        5. 清晰性：表达是否清晰易懂？结构是否合理？

        请返回JSON格式的评估结果：
        {{
            "is_passed": true/false,
            "confidence": 0-1,
            "feedback": "详细的评估意见，指出优点和不足",
            "suggestions": ["改进建议1", "改进建议2", "改进建议3"],
            "error_type": "具体错误类型（如：hallucination/fact_error/incomplete/off_topic）或 null"
        }}

        判断标准：
        - confidence >= {self.confidence_threshold} 视为通过
        - suggestions 最多提供 {self.max_suggestions} 条
        - error_type 可选值：null, "hallucination", "fact_error", "incomplete", "off_topic", "illogical", "unclear"
        """

        try:
            response = self.llm_client.chat.invoke([HumanMessage(content=prompt)])
            result = json.loads(response.content)
            
            # 验证结果格式
            return self._validate_result(result)
            
        except json.JSONDecodeError as e:
            exception(f"JSON解析失败: {e}", "Reflection", e)
            return self._create_fallback_result(answer)
        except Exception as e:
            exception(f"反思校验失败: {e}", "Reflection", e)
            return self._create_fallback_result(answer)

    def _validate_result(self, result: Dict) -> Dict[str, Any]:
        """
        验证并标准化校验结果
        
        Args:
            result: 原始校验结果
            
        Returns:
            标准化后的结果
        """
        # 确保必要字段存在
        is_passed = result.get("is_passed", False)
        confidence = result.get("confidence", 0.5)
        feedback = result.get("feedback", "")
        suggestions = result.get("suggestions", [])
        error_type = result.get("error_type", None)
        
        # 限制建议数量
        if len(suggestions) > self.max_suggestions:
            suggestions = suggestions[:self.max_suggestions]
        
        # 确保置信度在合理范围
        confidence = max(0.0, min(1.0, confidence))
        
        # 根据置信度调整通过状态
        if confidence >= self.confidence_threshold and not is_passed:
            is_passed = True
        elif confidence < self.confidence_threshold and is_passed:
            is_passed = False
        
        return {
            "is_passed": is_passed,
            "confidence": confidence,
            "feedback": feedback.strip(),
            "suggestions": suggestions,
            "error_type": error_type
        }

    def _create_fallback_result(self, answer: str) -> Dict[str, Any]:
        """
        创建降级校验结果
        
        Args:
            answer: 当前回答
            
        Returns:
            默认校验结果
        """
        if len(answer) < 20:
            return {
                "is_passed": False,
                "confidence": 0.5,
                "feedback": "校验过程中发生错误，回答可能不够详细",
                "suggestions": ["请提供更详细的回答"],
                "error_type": "validation_error"
            }
        
        return {
            "is_passed": True,
            "confidence": 0.7,
            "feedback": "校验过程中发生错误，默认通过",
            "suggestions": [],
            "error_type": None
        }

    def batch_reflect(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量校验多个回答
        
        Args:
            items: 待校验列表，每个元素包含 query, answer, documents(可选)
            
        Returns:
            校验结果列表
        """
        results = []
        for item in items:
            result = self.reflect(
                query=item["query"],
                answer=item["answer"],
                documents=item.get("documents")
            )
            results.append({**item, **result})
        return results
