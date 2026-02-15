from domain.schema.User import User

from repositories.UserRepository import UserRepository

from fastapi import Depends

#logic

class UserService :

    def __init__(self, repo : UserRepository = Depends()) :

        self.repo = repo

    def getCreateUser(self,newUser : User) :

        return self.repo.createUser(newUser)