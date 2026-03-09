from pydantic import BaseModel
# create domain
class User(BaseModel) :
    firstName : str
    lastName : str
    email : str
    address : str
    phoneNumber : str | None = None
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "firstName": "John"
                    ,"lastName": "Doe"
                    ,"email": "example@gmail.com"
                    ,"address": "some where"
                    ,"phoneNumber": "some number"
                }
            ]
        }
    }
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
