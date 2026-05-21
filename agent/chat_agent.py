from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Optional
from core.config import settings


class ChatAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL_NAME,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            temperature=settings.OPENAI_TEMPERATURE,
            streaming=True
        )

        try:
            from agent.tools import get_current_time, calculate
            self.tools = [get_current_time, calculate]
        except ImportError:
            self.tools = []
            print("警告: 无法导入工具函数")

        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt="你是江苏大学AI通识课助教。"
        )

    async def get_response_with_history(self, message: str, history_messages: List[dict]) -> str:
        """带历史记录的对话"""
        try:
            # 构建消息列表
            messages = []

            # 添加历史消息
            for msg in history_messages:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

            # 添加当前消息
            messages.append(HumanMessage(content=message))

            # 调用 agent
            response = await self.agent.ainvoke(
                {"messages": messages}
            )

            return response["messages"][-1].content
        except Exception as e:
            return f"抱歉，处理您的请求时出现错误: {str(e)}"

    async def get_response(self, message: str, session_id: str = "default") -> str:
        """兼容旧接口，不带历史"""
        return await self.get_response_with_history(message, [])