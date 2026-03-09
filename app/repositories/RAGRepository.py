from domain.orm.DomainORM import getConn, RagChatHistoryORM
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select, update, delete, text
from domain.schema.RagChatHistory import ChatHistoryUpdate
class RAGRepository :
    def __init__(self,db : Session = Depends(getConn)):
        self.db = db
    def create_chat_history(self, id: int):
        chat = RagChatHistoryORM(messages=[],user_id = id)
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat
    def find_by_user_id(self,id : int):
        stm = select(RagChatHistoryORM).where(RagChatHistoryORM.user_id == id)
        return self.db.scalar(stm)
    def find_by_id(self, id: int):
        stm = select(RagChatHistoryORM).where(RagChatHistoryORM.id == id)
        return self.db.scalar(stm)
    def update_chat_history(self, history: ChatHistoryUpdate):
        stm = update(RagChatHistoryORM).where(RagChatHistoryORM.id == history.id).values(
                    messages = history.messages)
        self.db.execute(stm)
        self.db.commit()
    def exist_by_chat_history_and_user_id (self,chat_id: int, user_id: int):
        stm = select(RagChatHistoryORM).where(RagChatHistoryORM.id == chat_id, RagChatHistoryORM.user_id == user_id)
        return True if self.db.scalar(stm) is not None else False
    def exist_by_collecton_name (self, collection_name : str) :
        result = self.db.execute(text("SELECT 1 FROM langchain_pg_collection WHERE name = :name"), {"name": collection_name})
        return True if result.fetchone() is not None else False