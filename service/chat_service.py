from typing import List, Dict, Optional
from agent.chat_agent import ChatAgent
from models.message import Message
from collections import defaultdict
import uuid


class LLMService:
    """LLM 服务类 - 简化版对话服务"""

    def __init__(self):
        self.agent = ChatAgent()
        # 存储对话历史（用于 API 返回）
        self.histories: Dict[str, List[Message]] = defaultdict(list)

    def create_session(self) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        self.histories[session_id] = []
        return session_id

    def get_conversation_history(self, session_id: str) -> List[Message]:
        """获取会话历史"""
        return self.histories.get(session_id, [])

    def clear_conversation(self, session_id: str):
        """清除会话"""
        if session_id in self.histories:
            self.histories[session_id] = []

    async def get_response(
            self,
            message: str,
            session_id: str
    ) -> str:
        """获取 agent 响应"""
        # 确保会话存在
        if session_id not in self.histories:
            self.create_session()

        # 调用 agent（LangGraph 自动管理记忆）
        response = await self.agent.get_response(message, session_id)

        # 保存到历史记录
        self.histories[session_id].append(Message(role="user", content=message))
        self.histories[session_id].append(Message(role="assistant", content=response))

        return response