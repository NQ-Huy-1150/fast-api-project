from fastapi import FastAPI
from contextlib import asynccontextmanager
from domain.orm.DomainORM import Base, engine
from controller.UserController import router as userRouter
from controller.LLMController import router as LLMRouter
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
