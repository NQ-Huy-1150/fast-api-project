from sqlalchemy import create_engine, text, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:123456@localhost/quanly"
engine = create_engine(DATABASE_URL,echo=True)
Session = sessionmaker(bind=engine)
#Depends
def getConn() :
    db = Session()
    try:
        yield db
    finally:
        db.close()

# ORM classes
Base = declarative_base()
class UserORM (Base) :
    __tablename__ = "users"
    id = Column(Integer,autoincrement = True, primary_key = True)
    fullName = Column("full_name",String)
    email = Column(String)
    address = Column(String)
    phoneNumber = Column("phone_number",String)