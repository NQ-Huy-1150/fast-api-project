from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from services.RAGService import RagService
from domain.schema.Ai import ChatRequest, ChatResponse
from domain.schema.ChatHistory import ChatHistoryResponse

router = APIRouter(prefix="/rag", tags=["RAG Engine"])
ai_service = Annotated[RagService, Depends()]

@router.post("/create_chat", response_model=ChatHistoryResponse)
def create_chat_history(user_id : int, service: ai_service):
    rs = service.get_create_chat(user_id)
    if rs is not None :
        return ChatHistoryResponse.model_validate(rs)
    else: raise HTTPException(status_code=404, detail={"Users": "Not Found"})

@router.post("/chat/{user_id}/{chat_id}/{collection_name}", response_model=ChatResponse)
def ask_llama(user_id : int, chat_id : int ,collection_name : str ,request: ChatRequest, service: ai_service):
    answer = service.ask(user_id, chat_id, collection_name, request)
    return {"answer": answer}