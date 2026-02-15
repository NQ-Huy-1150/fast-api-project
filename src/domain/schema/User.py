from pydantic import BaseModel
# create domain
class User(BaseModel) :
    firstName : str
    lastName : str
    email : str
    address : str
    phoneNumber : str | None = None
# return domain
class UserResponse(BaseModel) :
    id : int
    fullName : str
    email : str
    address : str
    phoneNumber : str | None = None
    class Config:
        from_attributes = True
# update domain
class UserUpdate(BaseModel) :
    firstName : str
    lastName : str
    address : str
    phoneNumber : str | None = None
