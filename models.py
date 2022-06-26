from sqlalchemy import Column,Integer,String
from database import Base

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



