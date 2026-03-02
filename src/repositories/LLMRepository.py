from domain.orm.DomainORM import getConn, ChatHistoryORM
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select, update, delete
from domain.schema.ChatHistory import ChatHistoryUpdate, ChatHistoryResponse
class LLMRepository :
    def __init__(self,db : Session = Depends(getConn)):
        self.db = db
    def create_chat_history(self, id: int):
        chat = ChatHistoryORM(messages=[],user_id = id)
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat
    def find_by_user_id(self,id : int):
        stm = select(ChatHistoryORM).where(ChatHistoryORM.user_id == id)
        return self.db.scalar(stm)
    def find_by_id(self, id: int):
        stm = select(ChatHistoryORM).where(ChatHistoryORM.id == id)
        return self.db.scalar(stm)
    def update_chat_history(self, history: ChatHistoryUpdate ):
        stm = update(ChatHistoryORM).where(ChatHistoryORM.id == history.id).values(
                    messages = history.messages)
        self.db.execute(stm)
        self.db.commit()
    def exist_by_chat_history_and_user_id (self,chat_id: int, user_id: int):
        stm = select(ChatHistoryORM).where(ChatHistoryORM.id == chat_id, ChatHistoryORM.user_id == user_id)
        return True if self.db.scalar(stm) is not None else False