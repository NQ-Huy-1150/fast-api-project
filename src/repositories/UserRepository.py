from domain.orm.DomainORM import getConn, UserORM
from sqlalchemy.orm import Session
from fastapi import Depends
from domain.schema.User import User
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
        #debug
        print(f">>>>>>>>> : {user}")