from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel, Field
from service.chat_service import LLMService

router = APIRouter(prefix="/api/chat", tags=["chat"])
llm_service = LLMService()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    try:
        session_id = request.session_id
        if not session_id:
            session_id = llm_service.create_session()

        response = await llm_service.get_response(request.message, session_id)
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    return {"history": llm_service.get_conversation_history(session_id)}