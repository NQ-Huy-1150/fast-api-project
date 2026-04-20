from domain.schema.User import User, UserUpdate

from repositories.UserRepository import UserRepository

from fastapi import Depends

#logic

class UserService :

    def __init__(self, repo : UserRepository = Depends()) :

        self.repo = repo

    async def getCreateUser(self,newUser : User) :
        return await self.repo.createUser(newUser)
    
    async def getUserById(self, id : int):
        return await self.repo.findUserById(id)
    
    async def fetchAllUser(self):
        return await self.repo.findAll()
    
    async def getUpdateUser(self,id : int, user : UserUpdate):
        return await self.repo.updateUser(id,user)
    
    async def isUserExisted(self, id : int):
        return await self.repo.ifUserWithIdExisted(id)
    
    async def getDeleteUser(self, id : int):
        return await self.repo.deleteUser(id)