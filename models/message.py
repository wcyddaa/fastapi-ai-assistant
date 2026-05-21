from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Message(BaseModel):
    """消息模型"""
    role: str = Field(..., description="消息角色: user/assistant/system")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="消息时间戳")
    message_id: Optional[str] = Field(None, description="消息ID")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "你好，请介绍一下自己",
                "timestamp": "2025-01-01T12:00:00",
                "message_id": "msg_123456"
            }
        }
