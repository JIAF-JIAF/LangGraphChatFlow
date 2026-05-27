"""
SSE 事件处理器
将 LangGraph 节点输出转换为 SSE 事件
"""

from typing import Callable


class SSEEventProcessor:
    """SSE 事件处理器：将 LangGraph 节点输出转换为 SSE 事件"""

    def __init__(self):
        self.final_answer = ""
        self.final_feeling = {"feeling": "default", "score": 5}
        self._handlers: dict[str, Callable] = {
            "call_model": self._handle_call_model,
            "feeling_detect": self._handle_feeling_detect,
            "retrieve": self._handle_retrieve,
            "plan": self._handle_plan,
            "execute_task": self._handle_execute_task,
        }

    def process_node(self, node_name: str, node_state: dict, session_id: str) -> dict | None:
        """处理单个节点，返回 SSE 事件数据"""
        handler = self._handlers.get(node_name, self._handle_unknown)
        return handler(node_name, node_state, session_id)

    def get_done_event(self, session_id: str) -> dict:
        """生成完成事件"""
        return {
            "type": "done",
            "session_id": session_id,
            "reply": self.final_answer,
            "feeling": self.final_feeling
        }

    def _handle_call_model(self, node_name: str, node_state: dict, session_id: str) -> dict | None:
        """处理 call_model 节点：提取增量 token"""
        answer = node_state.get("answer", "")
        if not answer:
            return None

        token = answer[len(self.final_answer):]
        if not token:
            return None

        self.final_answer = answer
        return {
            "type": "token",
            "node": node_name,
            "session_id": session_id,
            "content": token
        }

    def _handle_feeling_detect(self, node_name: str, node_state: dict, session_id: str) -> dict | None:
        """处理 feeling_detect 节点：提取情绪信息"""
        feeling = node_state.get("feeling")
        if not feeling:
            return None

        self.final_feeling = feeling
        return {
            "type": "feeling",
            "node": node_name,
            "session_id": session_id,
            "feeling": feeling
        }

    def _handle_retrieve(self, node_name: str, node_state: dict, session_id: str) -> dict | None:
        """处理 retrieve 节点：提取检索文档数量"""
        documents = node_state.get("documents", [])
        if not documents:
            return None

        return {
            "type": "retrieve",
            "node": node_name,
            "session_id": session_id,
            "doc_count": len(documents)
        }

    def _handle_plan(self, node_name: str, node_state: dict, session_id: str) -> dict | None:
        """处理 plan 节点：提取任务规划数量"""
        tasks = node_state.get("tasks", [])
        if not tasks:
            return None

        return {
            "type": "plan",
            "node": node_name,
            "session_id": session_id,
            "task_count": len(tasks)
        }

    def _handle_execute_task(self, node_name: str, node_state: dict, session_id: str) -> dict | None:
        """处理 execute_task 节点：提取任务执行结果"""
        task_result = node_state.get("task_result")
        if not task_result:
            return None

        return {
            "type": "task",
            "node": node_name,
            "session_id": session_id,
            "task": task_result
        }

    def _handle_unknown(self, node_name: str, node_state: dict, session_id: str) -> dict:
        """处理未知节点：返回通用节点更新"""
        return {
            "type": "node_update",
            "node": node_name,
            "session_id": session_id
        }
