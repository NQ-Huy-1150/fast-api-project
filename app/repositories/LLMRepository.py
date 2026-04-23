from domain.orm.DomainORM import ChatHistoryORM, get_async_conn
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy import select, update, delete
from domain.schema.ChatHistory import ChatHistoryUpdate, ChatHistoryResponse
class LLMRepository :
    def __init__(self,db : AsyncSession = Depends(get_async_conn)):
        self.db = db
    async def create_chat_history(self, id: int):
        async with self.db.begin() :
            chat = ChatHistoryORM(messages=[],user_id = id)
            self.db.add(chat)
        await self.db.refresh(chat)
        return chat
    async def find_by_user_id(self,id : int):
        stm = select(ChatHistoryORM).where(ChatHistoryORM.user_id == id)
        rs = await self.db.execute(stm)
        chat_histories = rs.scalars().all()
        return chat_histories
    async def find_by_id(self, id: int):
        stm = select(ChatHistoryORM).where(ChatHistoryORM.id == id)
        return await self.db.scalar(stm)
    async def update_chat_history(self, history: ChatHistoryUpdate ):
        stm = update(ChatHistoryORM).where(ChatHistoryORM.id == history.id).values(
                messages = history.messages)
        await self.db.execute(stm)
        await self.db.commit()
    async def exist_by_chat_history_and_user_id (self,chat_id: int, user_id: int):
        stm = select(ChatHistoryORM).where(ChatHistoryORM.id == chat_id, ChatHistoryORM.user_id == user_id)
        return True if await self.db.scalar(stm) is not None else False
    async def delete_chat_history(self,user_id : int, chat_id : int) :
        async with self.db.begin():
            stm = delete(ChatHistoryORM).where(ChatHistoryORM.id == chat_id, ChatHistoryORM.user_id == user_id)
            await self.db.execute(stm)