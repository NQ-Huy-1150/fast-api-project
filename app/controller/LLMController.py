from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from services.LLMService import AIService
from domain.schema.Ai import ChatRequest, ChatResponse
from domain.schema.ChatHistory import ChatHistoryResponse

router = APIRouter(prefix="/ai", tags=["AI Engine"])
ai_service = Annotated[AIService, Depends()]

@router.post("/create_chat", response_model=ChatHistoryResponse)
async def create_chat_history(user_id : int, service: ai_service):
    rs = await service.get_create_chat(user_id)
    if rs is not None :
        return ChatHistoryResponse.model_validate(rs)
    else: raise HTTPException(status_code=404, detail={"Users": "Not Found"})

@router.post("/chat/{user_id}/{chat_id}", response_model=ChatResponse)
async def ask_llama(user_id : int, chat_id : int ,request: ChatRequest, service: ai_service):
    answer = await service.ask(user_id, chat_id, request)
    return {"answer": answer}