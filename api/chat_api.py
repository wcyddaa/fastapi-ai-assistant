from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from service.chat_service import LLMService
from models.schemas import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    BatchChatRequest,
    SessionListResponse,
    DeleteMessageRequest,
    ErrorResponse,
    SessionInfo
)

router = APIRouter(prefix="/api/chat", tags=["chat"])
llm_service = LLMService()


@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    try:
        session_id = request.session_id
        if not session_id:
            session_id = llm_service.create_session()

        response = await llm_service.get_response(request.message, session_id)

        return ChatResponse(
            response=response,
            session_id=session_id,
            message_id=llm_service.get_last_message_id(session_id)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=List[ChatResponse])
async def send_batch_messages(request: BatchChatRequest):
    try:
        session_id = request.session_id
        if not session_id:
            session_id = llm_service.create_session()

        responses = []
        for message in request.messages:
            if message.role == "user":
                # 处理用户消息
                response = await llm_service.get_response(message.content, session_id)
                responses.append(ChatResponse(
                    response=response,
                    session_id=session_id,
                    message_id=llm_service.get_last_message_id(session_id)
                ))
            elif message.role == "assistant":
                # 可选：将历史助手消息添加到上下文
                # 但不生成响应
                llm_service.add_to_history(session_id, message)
            elif message.role == "system":
                # 可选：设置系统提示
                llm_service.set_system_prompt(session_id, message.content)

        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(
        session_id: str,
        limit: Optional[int] = Query(None, ge=1, le=100),
        offset: Optional[int] = Query(0, ge=0)
):
    try:
        messages = llm_service.get_conversation_history(session_id, limit=limit, offset=offset)
        total_count = llm_service.get_message_count(session_id)

        return HistoryResponse(
            session_id=session_id,
            messages=messages,
            total_count=total_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100)
):
    try:
        sessions = llm_service.get_all_sessions(page=page, page_size=page_size)
        total = llm_service.get_session_count()

        session_info_list = [SessionInfo(**session) for session in sessions]

        return SessionListResponse(
            sessions=session_info_list,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/message", response_model=dict)
async def delete_message(request: DeleteMessageRequest):
    try:
        success = llm_service.delete_message(request.session_id, request.message_id)
        if not success:
            raise HTTPException(status_code=404, detail="Message not found")

        return {"success": True, "message": "Message deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/info", response_model=SessionInfo)
async def get_session_info(session_id: str):
    try:
        info = llm_service.get_session_info(session_id)
        if not info:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionInfo(**info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    try:
        success = llm_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"success": True, "message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))