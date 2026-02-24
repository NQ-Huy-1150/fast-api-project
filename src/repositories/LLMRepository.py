from domain.orm.DomainORM import getConn
from sqlalchemy.orm import Session
from fastapi import Depends

class LLMRepository :
    def __init__(self,db : Session = Depends(getConn)):
        self.db = db