from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class Message(BaseModel):
    """单条消息模型"""
    role: str = Field(..., description="消息角色: user/assistant/system")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="消息时间戳")
    message_id: Optional[str] = Field(None, description="消息ID")


class ChatRequest(BaseModel):
    """聊天请求数据模型"""
    message: str = Field(..., min_length=1, description="用户消息内容")
    session_id: Optional[str] = Field(None, description="会话ID，可选")
    stream: bool = Field(False, description="是否流式输出")


class BatchChatRequest(BaseModel):
    """批量聊天请求数据模型"""
    messages: List[Message] = Field(..., min_length=1, description="消息列表")
    session_id: Optional[str] = Field(None, description="会话ID，可选")


class ChatResponse(BaseModel):
    """聊天响应数据模型"""
    response: str = Field(..., description="AI返回的响应内容")
    session_id: str = Field(..., description="会话ID")
    message_id: Optional[str] = Field(None, description="响应消息ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")


class HistoryResponse(BaseModel):
    """历史记录响应数据模型"""
    session_id: str = Field(..., description="会话ID")
    messages: List[Message] = Field(..., description="对话历史消息列表")
    total_count: int = Field(..., description="总消息数")


class SessionInfo(BaseModel):
    """会话信息模型"""
    session_id: str = Field(..., description="会话ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")
    message_count: int = Field(..., description="消息数量")


class SessionListResponse(BaseModel):
    """会话列表响应模型"""
    sessions: List[SessionInfo] = Field(..., description="会话列表")
    total: int = Field(..., description="总会话数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(20, description="每页数量")


class DeleteMessageRequest(BaseModel):
    """删除消息请求模型"""
    message_id: str = Field(..., description="要删除的消息ID")
    session_id: str = Field(..., description="所属会话ID")


class ErrorResponse(BaseModel):
    """统一错误响应模型"""
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细错误描述")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误发生时间")