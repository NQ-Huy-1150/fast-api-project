from fastapi import FastAPI, HTTPException, Depends
from domain.schema.User import User, UserUpdate, UserResponse
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

@app.get("/")
async def homepage() :
    return "hello"
@app.get("/user/{id}", response_model=UserResponse)
def getUserDetail(id : int, userService : UserService = Depends()) :
    rs = userService.getUserById(id)
    if rs is not None :
        return rs
    else: raise HTTPException(status_code=404, detail={"User": "Not Found"})

@app.get("/users",response_model=list[UserResponse])
def getAllUser(userService : UserService = Depends()):
    rs = userService.fetchAllUser()
    if rs is not None :
        return rs
    else: raise HTTPException(status_code=404, detail={"Users": "Not Found"})


@app.post("/register")
def register(creUser : User, userService : UserService = Depends()) :
    if creUser is not None :
        rs = userService.getCreateUser(creUser)
        return {"message": "Created", "user": rs}
    else: raise HTTPException(status_code=500, detail="some thing wrong !")

@app.put("/update-user/{id}")
def updateUser(id : int,currentUser : UserUpdate, userService : UserService = Depends()) :
    if userService.isUserExisted(id) :
        userService.getUpdateUser(id,currentUser)
        return {"message": "Update Successfully !"}
    else: raise HTTPException(status_code=404, detail={"Users": "Not Found"})

@app.delete("/delete-user/{id}")
def deleteUser(id : int, userService : UserService = Depends()):
    if userService.isUserExisted(id) :
        userService.getDeleteUser(id)
        return {"message": "Delete Successfully !"}
    else: raise HTTPException(status_code=404, detail={"Users": "Not Found"})