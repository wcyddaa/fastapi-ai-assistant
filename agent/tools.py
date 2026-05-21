# agents/tools.py
from langchain.tools import tool
from datetime import datetime

@tool
def get_current_time() -> str:
    """获取当前日期和时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def calculate(expression: str) -> float:
    """计算数学表达式"""
    return eval(expression)