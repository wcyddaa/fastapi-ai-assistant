from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from typing import AsyncGenerator
from core.config import settings  # 直接导入配置


class ChatAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL_NAME,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            temperature=settings.OPENAI_TEMPERATURE,
            streaming=True
        )

        # 定义工具
        try:
            from agent.tools import get_current_time, calculate
            self.tools = [get_current_time, calculate]
        except ImportError:
            self.tools = []
            print("警告: 无法导入工具函数")

        # 创建 agent
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt="你是一个有帮助的智能助手。"
        )

    async def get_response(self, message: str, session_id: str = "default") -> str:
        """获取 agent 响应"""
        try:
            response = await self.agent.ainvoke(
                {"messages": [HumanMessage(content=message)]},
                config={"configurable": {"thread_id": session_id}}
            )
            return response["messages"][-1].content
        except Exception as e:
            return f"抱歉，处理您的请求时出现错误: {str(e)}"