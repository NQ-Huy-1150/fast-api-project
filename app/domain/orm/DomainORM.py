import os
from sqlalchemy import create_engine, text, Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import JSONB
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None :
    raise ValueError("Cant connect to Database !")
engine = create_engine(DATABASE_URL,echo=True)
Session = sessionmaker(bind=engine)
#Depends
def getConn() :
    db = Session()
    try:
        yield db
    finally:
        db.close()

# ORM classes
class Base(DeclarativeBase) :
    pass
class UserORM (Base) :
    __tablename__ = "users"
    id = Column(Integer,autoincrement = True, primary_key = True)
    fullName = Column("full_name",String)
    email = Column(String)
    address = Column(String)
    phoneNumber = Column("phone_number",String)
    chats = relationship("ChatHistoryORM", back_populates="user")
    rag_chat = relationship("RagChatHistoryORM", back_populates="user")
class ChatHistoryORM (Base):
    __tablename__ = "chat_histories"
    id = Column(Integer,autoincrement = True, primary_key = True)
    user_id = Column(Integer, ForeignKey("users.id"))
    messages = Column(JSONB, default=list)
    user = relationship("UserORM", back_populates="chats")
class RagChatHistoryORM (Base):
    __tablename__ = "rag_chat_histories"
    id = Column(Integer,autoincrement = True, primary_key = True)
    user_id = Column(Integer, ForeignKey("users.id"))
    messages = Column(JSONB, default=list)
    user = relationship("UserORM", back_populates="rag_chat")
