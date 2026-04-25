from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from services.RAGService import RagService
from domain.schema.Ai import ChatRequest, ChatResponse
from domain.schema.ChatHistory import ChatHistoryResponse

router = APIRouter(prefix="/rag", tags=["RAG Engine"])
ai_service = Annotated[RagService, Depends()]

@router.post("/create_chat", response_model=ChatHistoryResponse)
async def create_chat_history(user_id : int, service: ai_service):
    rs = await service.get_create_chat(user_id)
    if rs is not None :
        return ChatHistoryResponse.model_validate(rs)
    else: raise HTTPException(status_code=404, detail={"Users": "Not Found"})

@router.post("/ask_ollama/{user_id}/{chat_id}/{collection_name}", response_model=ChatResponse)
async def ask_llama(user_id: int, chat_id: int, collection_name: str, request: ChatRequest, service: ai_service):
    answer = await service.ask(user_id, chat_id, collection_name, request)
    return {"answer": answer}

@router.post("/chat_with_base_crag", response_model=ChatResponse)
async def ask_with_base_crag(collection_name: str, request: ChatRequest, service: ai_service):
    answer = await service.ask_with_base_crag(collection_name, request)
    return {"answer": answer}

@router.get("/chats/{user_id}",response_model=list[ChatHistoryResponse])
async def fetch_all_chat(user_id : int, service : ai_service) :
    chat_histories =  await service.get_chat_histories_by_user_id(user_id)
    if chat_histories is not None :
        return chat_histories
    else : raise HTTPException(status_code=404, detail="Histories with user_id not found !")
@router.delete("/delete/{id}")
async def delete_history(id : int, service: ai_service):
    is_deleted = service.get_delete(id)
    if not is_deleted:
        raise HTTPException(status_code=404,detail="Chat history with id not found !")
    return {"status" : "success"}