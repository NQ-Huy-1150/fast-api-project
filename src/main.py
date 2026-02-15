from fastapi import FastAPI, HTTPException, Depends
from domain.schema.User import User
from contextlib import asynccontextmanager
from domain.orm.DomainORM import Base, engine
from services.UserService import UserService
#pre setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    #check / create table
    print("Starting up...")
    Base.metadata.create_all(bind=engine,checkfirst=True)
    print("Database tables created!")
    yield
    print("Shutting down...")

#application
app = FastAPI(lifespan=lifespan)
users = []

@app.get("/")
async def homepage() :
    return "hello"
@app.get("/user/{userId}")
def getUserDetail(userId : int) :
    for user in users :
        print(f">>>>>>>> user id : {userId}")
        if user.id == userId : return user
    return {"User" : "Not Found!"}

@app.post("/register")
def register(creUser : User, userService : UserService = Depends()) :
    if creUser != None :
        userService.getCreateUser(creUser)
        return {"message": "Created", "user": creUser}
    else: raise HTTPException(status_code=500, detail="some thing wrong !")

@app.put("/update-user")
def updateUser(currentUser : User) :
    if currentUser != None :
        for user in users :
            if user.id == currentUser :
                #user.fullName = currentUser.fullName
                user.email = currentUser.email
                user.address = currentUser.address
                user.phoneNumber = currentUser.phoneNumber
                return user
            else : return {"id": "Not Found!"}
    return "Some errors occur !"
@app.delete("/delete-user")
def deleteUser(userId : int):
    for user in users :
        if user.id == userId :
            users.remove(user)
            return users
        else : return {"id": "Not Found!"}
    return "Some errors occur !"