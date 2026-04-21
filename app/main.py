import os
import httpx
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import text
from domain.orm.DomainORM import Base, async_engine
from controller.UserController import router as userRouter
from controller.LLMController import router as LLMRouter
from controller.ItemController import router as item_router
from controller.RAGController import router as Rag_router
from controller.WebSocketController import router as websocket_router
from dotenv import load_dotenv

load_dotenv()


# async def check_ollama_ready() -> None:
#     ollama_base_url = os.getenv("OLLAMA_BASE_URL").rstrip("/")
#     ollama_model = os.getenv("OLLAMA_MODEL")
#     timeout = httpx.Timeout(4.0)
#     tags_url = f"{ollama_base_url}/api/tags"

#     try:
#         async with httpx.AsyncClient(timeout=timeout) as client:
#             response = await client.get(tags_url)
#             response.raise_for_status()
#             payload = response.json()
#     except httpx.HTTPError as exc:
#         raise RuntimeError(
#             "Cannot connect to Ollama at "
#             f"{ollama_base_url}. Please start Ollama and verify OLLAMA_BASE_URL. "
#             "Example fix: run 'ollama serve' or open the Ollama app."
#         ) from exc

#     models = payload.get("models", []) if isinstance(payload, dict) else []
#     available_names = [model.get("name", "") for model in models if isinstance(model, dict)]
#     if not any(name == ollama_model or name.startswith(f"{ollama_model}:") for name in available_names):
#         model_list = ", ".join(available_names) if available_names else "none"
#         raise RuntimeError(
#             f"Ollama is running but model '{ollama_model}' is not available. "
#             f"Installed models: {model_list}. "
#             f"Example fix: run 'ollama pull {ollama_model}'."
#         )

#     print(f"Ollama check passed: {ollama_base_url}, model={ollama_model}")

#pre setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    #check / create table
    print("Starting up...")
    # await check_ollama_ready()
    async with async_engine.begin() as conn :
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created!")
    yield
    print("Shutting down...")

#application
app = FastAPI(lifespan=lifespan)
app.include_router(userRouter)
app.include_router(LLMRouter)
app.include_router(item_router)
app.include_router(Rag_router)
app.include_router(websocket_router)