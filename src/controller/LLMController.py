from fastapi import APIRouter, Depends
from typing import Annotated
from services.LLMService import AIService
from domain.schema.Ai import ChatRequest, ChatResponse

router = APIRouter(prefix="/ai", tags=["AI Engine"])
ai_service = Annotated[AIService, Depends()]

@router.post("/ask", response_model=ChatResponse)
async def ask_llama(request: ChatRequest, service: ai_service):
    answer = await service.ask(request)
    return {"answer": answer}