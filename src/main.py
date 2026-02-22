from fastapi import FastAPI, HTTPException, Depends, Path, Query
from typing import Annotated
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
# DI
userService = Annotated[UserService, Depends()]
# Custom variable
customId = Annotated[int, Path(title="The id of the user", gt=0)]
@app.get("/")
async def homepage() :
    return "hello"
@app.get("/user/{id}", response_model=UserResponse)
def getUserDetail(service : userService, id : customId) :
    rs = service.getUserById(id)
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
def register(creUser : User , service : userService) :
    if creUser is not None :
        rs = service.getCreateUser(creUser)
        return {"message": "Created", "user": rs}
    else: raise HTTPException(status_code=500, detail="some thing wrong !")

@app.put("/update-user/{id}")
def updateUser(id : customId, currentUser : UserUpdate, service : userService) :
    if service.isUserExisted(id) :
        service.getUpdateUser(id,currentUser)
        return {"message": "Update Successfully !"}
    else: raise HTTPException(status_code=404, detail={"Users": "Not Found"})

@app.delete("/delete-user/{id}")
def deleteUser(id : customId, service : userService):
    if service.isUserExisted(id) :
        service.getDeleteUser(id)
        return {"message": "Delete Successfully !"}
    else: raise HTTPException(status_code=404, detail={"Users": "Not Found"})

@app.get("/new-year")
def happy_new_year() :
    return {"message": "Chào mừng xuân bính ngọ 2026 !"}