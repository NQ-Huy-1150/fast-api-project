from domain.schema.User import User, UserUpdate

from repositories.UserRepository import UserRepository

from fastapi import Depends

#logic

class UserService :

    def __init__(self, repo : UserRepository = Depends()) :

        self.repo = repo

    def getCreateUser(self,newUser : User) :
        return self.repo.createUser(newUser)
    
    def getUserById(self, id : int):
        return self.repo.findUserById(id)
    
    def fetchAllUser(self):
        return self.repo.findAll()
    
    def getUpdateUser(self,id : int, user : UserUpdate):
        return self.repo.updateUser(id,user)
    
    def isUserExisted(self, id : int):
        return self.repo.ifUserWithIdExisted(id)
    
    def getDeleteUser(self, id : int):
        return self.repo.deleteUser(id)