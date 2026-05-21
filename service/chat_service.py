from typing import List, Dict, Optional
from agent.chat_agent import ChatAgent
from models.schemas import Message, SessionInfo
from collections import defaultdict
import uuid
from datetime import datetime


class LLMService:
    def __init__(self):
        self.agent = ChatAgent()
        self.histories: Dict[str, List[Message]] = defaultdict(list)
        self.sessions_meta: Dict[str, dict] = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.histories[session_id] = []
        self.sessions_meta[session_id] = {
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "message_count": 0
        }
        return session_id

    def _convert_history_to_dict(self, session_id: str) -> List[dict]:
        """将 Message 对象转换为字典格式供 Agent 使用"""
        history_dicts = []
        for msg in self.histories[session_id]:
            history_dicts.append({
                "role": msg.role,
                "content": msg.content
            })
        return history_dicts

    def add_to_history(self, session_id: str, message: Message) -> None:
        """添加消息到历史记录（用于批量处理中的 assistant 消息）"""
        if session_id not in self.histories:
            self.create_session()

        # 确保消息有 message_id
        if not message.message_id:
            message.message_id = str(uuid.uuid4())

        # 确保有时间戳
        if not message.timestamp:
            message.timestamp = datetime.now()

        self.histories[session_id].append(message)

        # 更新会话元信息
        if session_id in self.sessions_meta:
            self.sessions_meta[session_id]["updated_at"] = datetime.now()
            self.sessions_meta[session_id]["message_count"] = len(self.histories[session_id])

    def set_system_prompt(self, session_id: str, content: str) -> None:
        """设置系统提示（添加到历史记录开头）"""
        if session_id not in self.histories:
            self.create_session()

        system_message = Message(
            role="system",
            content=content,
            message_id=str(uuid.uuid4())
        )

        # 如果已经有系统消息，替换它
        for i, msg in enumerate(self.histories[session_id]):
            if msg.role == "system":
                self.histories[session_id][i] = system_message
                return

        # 否则添加到开头
        self.histories[session_id].insert(0, system_message)

    async def get_response(self, message: str, session_id: str) -> str:
        if session_id not in self.histories:
            self.create_session()

        # 获取历史消息（转换为字典格式）
        history = self._convert_history_to_dict(session_id)

        # 生成用户消息ID
        user_message_id = str(uuid.uuid4())
        user_message = Message(
            role="user",
            content=message,
            message_id=user_message_id
        )
        self.histories[session_id].append(user_message)

        # 调用 agent，传入历史记录
        response = await self.agent.get_response_with_history(message, history)

        # 生成助手消息ID
        assistant_message_id = str(uuid.uuid4())
        assistant_message = Message(
            role="assistant",
            content=response,
            message_id=assistant_message_id
        )
        self.histories[session_id].append(assistant_message)

        # 更新会话元信息
        if session_id in self.sessions_meta:
            self.sessions_meta[session_id]["updated_at"] = datetime.now()
            self.sessions_meta[session_id]["message_count"] = len(self.histories[session_id])

        return response

    def get_conversation_history(self, session_id: str, limit: Optional[int] = None, offset: int = 0) -> List[Message]:
        """获取会话历史"""
        messages = self.histories.get(session_id, [])

        if limit is not None:
            start = offset
            end = offset + limit
            messages = messages[start:end]

        return messages

    def get_message_count(self, session_id: str) -> int:
        return len(self.histories.get(session_id, []))

    def get_last_message_id(self, session_id: str) -> Optional[str]:
        messages = self.histories.get(session_id, [])
        if messages:
            return messages[-1].message_id
        return None

    def clear_conversation(self, session_id: str):
        if session_id in self.histories:
            self.histories[session_id] = []
            if session_id in self.sessions_meta:
                self.sessions_meta[session_id]["message_count"] = 0
                self.sessions_meta[session_id]["updated_at"] = datetime.now()

    def delete_session(self, session_id: str) -> bool:
        if session_id in self.histories:
            del self.histories[session_id]
            if session_id in self.sessions_meta:
                del self.sessions_meta[session_id]
            return True
        return False

    def delete_message(self, session_id: str, message_id: str) -> bool:
        if session_id not in self.histories:
            return False

        messages = self.histories[session_id]
        initial_length = len(messages)

        self.histories[session_id] = [msg for msg in messages if msg.message_id != message_id]

        if len(self.histories[session_id]) < initial_length:
            if session_id in self.sessions_meta:
                self.sessions_meta[session_id]["message_count"] = len(self.histories[session_id])
                self.sessions_meta[session_id]["updated_at"] = datetime.now()
            return True

        return False

    def get_session_info(self, session_id: str) -> Optional[dict]:
        if session_id not in self.histories:
            return None

        meta = self.sessions_meta.get(session_id, {})
        return {
            "session_id": session_id,
            "created_at": meta.get("created_at", datetime.now()),
            "updated_at": meta.get("updated_at", datetime.now()),
            "message_count": len(self.histories[session_id])
        }

    def get_all_sessions(self, page: int = 1, page_size: int = 20) -> List[dict]:
        sessions = []
        for session_id, messages in self.histories.items():
            meta = self.sessions_meta.get(session_id, {})
            sessions.append({
                "session_id": session_id,
                "created_at": meta.get("created_at", datetime.now()),
                "updated_at": meta.get("updated_at", datetime.now()),
                "message_count": len(messages)
            })

        sessions.sort(key=lambda x: x["updated_at"], reverse=True)

        start = (page - 1) * page_size
        end = start + page_size
        return sessions[start:end]

    def get_session_count(self) -> int:
        return len(self.histories)