from domain.orm.DomainORM import getConn, UserORM
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from fastapi import Depends
from domain.schema.User import User, UserUpdate, UserResponse
class UserRepository :
    def __init__(self, db : Session = Depends(getConn)):
        self.db = db
    def createUser(self,currentUser: User) :
        user = UserORM(fullName = currentUser.firstName + " " + currentUser.lastName
                   ,email = currentUser.email
                   ,address = currentUser.address
                   ,phoneNumber = currentUser.phoneNumber)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def findUserById(self,id : int) :
        stm = select(UserORM).where(UserORM.id == id)
        return self.db.scalar(stm)
    
    def findAll(self):
        stm = select(UserORM)
        return self.db.scalars(stm).all()
    
    def updateUser(self, id : int , user : UserUpdate) :
        stm = update(UserORM).where(UserORM.id == id).values(
                    fullName = user.firstName + " " + user.lastName
                   ,address = user.address
                   ,phoneNumber = user.phoneNumber)
        self.db.execute(stm)
        self.db.commit()

    def ifUserWithIdExisted(self, id : int):
        return self.db.scalar(select(UserORM).where(UserORM.id == id)) is not None
    
    def deleteUser(self, id : int):
        stm = delete(UserORM).where(UserORM.id == id)
        self.db.execute(stm)
        self.db.commit()