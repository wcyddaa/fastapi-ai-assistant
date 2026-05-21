import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

# 加载 .env 文件
load_dotenv()


class Settings(BaseSettings):
    """应用配置类 - 使用 Pydantic"""

    # ========== 基础配置 ==========
    APP_NAME: str = "FastAPI AI Assistant"
    DEBUG: bool = False
    API_V1_STR: str = "/api"

    # ========== AI 模型配置（通义千问） ==========
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    OPENAI_MODEL_NAME: str = "qwen3-max"
    OPENAI_TEMPERATURE: float = 0.1

    # ========== 会话配置 ==========
    MAX_HISTORY_LENGTH: int = 50

    class Config:
        # 允许从环境变量读取
        env_file = ".env"
        env_file_encoding = "utf-8"


# 创建全局配置实例
settings = Settings()