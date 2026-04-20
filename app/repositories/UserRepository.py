from domain.orm.DomainORM import UserORM, get_async_conn
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from domain.schema.User import User, UserUpdate
class UserRepository :
    def __init__(self, db : AsyncSession = Depends(get_async_conn)):
        self.db = db
    async def createUser(self,currentUser: User) :
        async with self.db.begin() :
            user = UserORM(fullName = currentUser.firstName + " " + currentUser.lastName
                    ,email = currentUser.email
                    ,address = currentUser.address
                    ,phoneNumber = currentUser.phoneNumber)
            self.db.add(user)
        await self.db.refresh(user)
        return user
    
    async def findUserById(self,id : int) :
        stm = select(UserORM).where(UserORM.id == id)
        return await self.db.scalar(stm)
    
    async def findAll(self):
        stm = select(UserORM)
        rs = await self.db.execute(stm)
        users = rs.scalars().all()
        return users
    
    async def updateUser(self, id : int , user : UserUpdate) :
        async with self.db.begin() :
            stm = update(UserORM).where(UserORM.id == id).values(
                        fullName = user.firstName + " " + user.lastName
                    ,address = user.address
                    ,phoneNumber = user.phoneNumber)
            await self.db.execute(stm)

    async def ifUserWithIdExisted(self, id : int):
        return await self.db.scalar(select(UserORM).where(UserORM.id == id)) is not None
    
    async def deleteUser(self, id : int):
        async with self.db.begin():
            stm = delete(UserORM).where(UserORM.id == id)
            await self.db.execute(stm)