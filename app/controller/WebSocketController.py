from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect, status
from typing import Annotated, cast
from services.LLMService import AIService
from services.RAGService import RagService
from domain.schema.Ai import ChatRequest
router = APIRouter(prefix="/ws", tags=["WebSocket"])
ai_service = Annotated[AIService, Depends()]
rag_service = Annotated[RagService, Depends()]
@router.websocket("/test")
async def websocket_endpoint(websocket : WebSocket) :
    await websocket.accept()
    try:
        while True :
            data = await websocket.receive_text()
            response = f"Hello from fastapi. Recieved message \"{data}\" successfully !"
            await websocket.send_text(response)
    except WebSocketDisconnect:
        return
    except Exception:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

@router.websocket("/chat/{user_id}/{chat_id}")
async def chat_with_ollama(user_id : int, chat_id : int, service : ai_service, websocket : WebSocket) :
    await websocket.accept()
    try:
        while True :
            request_text = await websocket.receive_text()
            chat_request = ChatRequest(prompt=request_text, model_name="Ollama3.2")
            response = await service.ask(user_id, chat_id, chat_request)
            await websocket.send_text(cast(str,response))
    except WebSocketDisconnect:
        return
    except Exception:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

@router.websocket("/rag/{user_id}/{chat_id}")
async def chat_with_rag(user_id : int, chat_id : int, service : rag_service, websocket : WebSocket):
    await websocket.accept()
    try:
        while True :
            request_text = await websocket.receive_text()
            chat_request = ChatRequest(prompt=request_text, model_name="")
            response = await service.ask(user_id, chat_id,"hanoi_knowledge_base_semantic" ,chat_request)
            await websocket.send_text(cast(str,response))
    except WebSocketDisconnect:
        return
    except Exception:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)