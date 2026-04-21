from domain.orm.DomainORM import RagChatHistoryORM, get_async_conn
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy import select, update, delete, text
from domain.schema.RagChatHistory import ChatHistoryUpdate
class RAGRepository :
    def __init__(self,db : AsyncSession = Depends(get_async_conn)):
        self.db = db
    async def create_chat_history(self, id: int):
        async with self.db.begin():
            chat = RagChatHistoryORM(messages=[],user_id = id)
            self.db.add(chat)
        await self.db.refresh(chat)
        return chat
    async def find_by_user_id(self,id : int):
        stm = select(RagChatHistoryORM).where(RagChatHistoryORM.user_id == id)
        rs = await self.db.execute(stm)
        rag_chat_histories = rs.scalars().all()
        return rag_chat_histories
    async def find_by_id(self, id: int):
        stm = select(RagChatHistoryORM).where(RagChatHistoryORM.id == id)
        return await self.db.scalar(stm)
    async def update_chat_history(self, history: ChatHistoryUpdate):
        stm = update(RagChatHistoryORM).where(RagChatHistoryORM.id == history.id).values(
            messages = history.messages)
        await self.db.execute(stm)
        await self.db.commit()
    async def exist_by_chat_history_and_user_id (self,chat_id: int, user_id: int):
        stm = select(RagChatHistoryORM).where(RagChatHistoryORM.id == chat_id, RagChatHistoryORM.user_id == user_id)
        return True if await self.db.scalar(stm) is not None else False
    async def exist_by_collecton_name (self, collection_name : str) :
        result = await self.db.execute(text("SELECT 1 FROM langchain_pg_collection WHERE name = :name"), {"name": collection_name})
        return True if result.fetchone() is not None else False
    async def delete_by_id (self, id : int) :
        try:
            async with self.db.begin():
                stm = delete(RagChatHistoryORM).where(RagChatHistoryORM.id == id).returning(RagChatHistoryORM.id)
                rs = await self.db.execute(stm)
                deleted_id = rs.scalar_one_or_none()
                if deleted_id is None :
                    return False
                return True
        except Exception as e:
            print(f"Error: {e}")
            return False