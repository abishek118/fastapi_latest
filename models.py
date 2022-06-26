from sqlalchemy import Column,Integer,String
from database import Base

#created a table in in database
class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index = True)
    streetAddress=Column(String)
    city=Column(String)
    state=Column(String)
    country=Column(String)
    pincode=Column(Integer)
    coordinates = Column(String)
    mapUrl=Column(String)



