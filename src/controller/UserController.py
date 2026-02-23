from fastapi import HTTPException, Depends, Path, Header, Cookie, APIRouter
from typing import Annotated
from domain.schema.User import User, UserUpdate, UserResponse
from services.UserService import UserService

# setup router
router = APIRouter()
# DI
userService = Annotated[UserService, Depends()]
# Custom variable
customId = Annotated[int, Path(title="The id of the user", gt=0)]
@router.get("/")
async def homepage() :
    return "hello"
@router.get("/user/{id}", response_model=UserResponse)
def getUserDetail(service : userService, id : customId) :
    rs = service.getUserById(id)
    if rs is not None :
        return rs
    else: raise HTTPException(status_code=404, detail={"User": "Not Found"})

@router.get("/users",response_model=list[UserResponse])
def getAllUser(userService : UserService = Depends()):
    rs = userService.fetchAllUser()
    if rs is not None :
        return rs
    else: raise HTTPException(status_code=404, detail={"Users": "Not Found"})


@router.post("/register")
def register(creUser : User , service : userService) :
    if creUser is not None :
        rs = service.getCreateUser(creUser)
        return {"message": "Created", "user": rs}
    else: raise HTTPException(status_code=500, detail="some thing wrong !")

@router.put("/update-user/{id}")
def updateUser(id : customId, currentUser : UserUpdate, service : userService) :
    if service.isUserExisted(id) :
        service.getUpdateUser(id,currentUser)
        return {"message": "Update Successfully !"}
    else: raise HTTPException(status_code=404, detail={"Users": "Not Found"})

@router.delete("/delete-user/{id}")
def deleteUser(id : customId, service : userService):
    if service.isUserExisted(id) :
        service.getDeleteUser(id)
        return {"message": "Delete Successfully !"}
    else: raise HTTPException(status_code=404, detail={"Users": "Not Found"})

@router.get("/new-year")
def happy_new_year() :
    return {"message": "Chào mừng xuân bính ngọ 2026 !"}
@router.get("/items/")
# Get header and cookie
async def read_items(user_agent: Annotated[str | None, Header()] = None, ads_id: Annotated[str | None, Cookie()] = None):
    return {"User-Agent": user_agent, "Ads-id": ads_id}