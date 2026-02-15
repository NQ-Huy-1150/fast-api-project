from pydantic import BaseModel
class User(BaseModel) :
    firstName : str
    lastName : str
    email : str
    address : str
    phoneNumber : str | None = None
