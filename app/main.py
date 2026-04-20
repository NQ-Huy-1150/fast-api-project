from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import text
from domain.orm.DomainORM import Base, async_engine
from controller.UserController import router as userRouter
from controller.LLMController import router as LLMRouter
from controller.ItemController import router as item_router
from controller.RAGController import router as Rag_router
from controller.WebSocketController import router as websocket_router
#pre setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    #check / create table
    print("Starting up...")
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