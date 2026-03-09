from fastapi import FastAPI
from contextlib import asynccontextmanager
from domain.orm.DomainORM import Base, engine
from controller.UserController import router as userRouter
from controller.LLMController import router as LLMRouter
from controller.ItemController import router as item_router
from controller.RAGController import router as Rag_router
#pre setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    #check / create table
    print("Starting up...")
    Base.metadata.create_all(bind=engine,checkfirst=True)
    print("Database tables created!")
    yield
    print("Shutting down...")

#application
app = FastAPI(lifespan=lifespan)
app.include_router(userRouter)
app.include_router(LLMRouter)
app.include_router(item_router)
app.include_router(Rag_router)