from fastapi import FastAPI,HTTPException,Depends
from pydantic import BaseModel, Field
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from geopy import distance
import coordinates
import models
import logging

logger = logging.getLogger(__name__)

# level and the format
logger.setLevel(logging.DEBUG)
f = logging.Formatter('%(asctime)s%(levelname)s-%(name)s-%(message)s')

# create handler logger
fh=logging.FileHandler('address.log')
fh.setFormatter(f)

logger.addHandler(fh)

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    try:
        db =SessionLocal()
        yield db
    finally:
        db.close()

class Address_Book(BaseModel):
    
    streetAddress:str = Field(min_length=1,max_length=100)
    city:str = Field(min_length=1,max_length=50)
    state:str = Field(min_length=1,max_length=50)
    country:str = Field(min_length=1,max_length=50)
    pincode:int = Field()


ADDRESS = []

# Post the location address and coordinates into Database 
@app.post("/")
def create_address(address:Address_Book, db:Session = Depends(get_db)):
    # getting the location address
    address_model = models.Address()
    address_model.streetAddress = address.streetAddress
    address_model.city = address.city
    address_model.state = address.state
    address_model.country = address.country
    address_model.pincode = address.pincode
    # getting coordinate data from mapquest api in the coordinates.py file 
    
    full_add_data=coordinates.coordinates(f"{address_model.streetAddress},{address_model.city},{address_model.state}")
    logger.debug(f"{full_add_data}")
    address_model.coordinates = f"{full_add_data[0]},{full_add_data[1]}"
    address_model.mapUrl = full_add_data[2]

    
   
    db.add(address_model)#adding to the database
    db.commit() # committing the changes to the database
    logger.info(f"Address created Sucessfully")
    return address

# Get all address
@app.get("/")
def read_api(db: Session = Depends(get_db)):
    # get all the address data from database and return to user
    return db.query(models.Address).all() 


# Get all data under the given radius in km from given address in parameter 
@app.get("/nearby/{distance_in_km}/{street}/{city}/{state}")
def read_api(distance_in_km:float,street:str,city:str,state:str,db: Session = Depends(get_db)):
    #detting coordinate data and converting string to float
    coordinates_loc = coordinates.coordinates(street+","+city+","+state)
    lat,lon=coordinates_loc.split(",")
    lat,lon= float(lat),float(lon)
    all_data=db.query(models.Address).all()

    near_by = []
    # checking the data is <= the given distance and appending to above array
    for single_add in all_data:
        cal_dis = distance.distance((lat,lon), ([float(x) for x in single_add.coordinates.split(",")])).km
        given_dis = distance_in_km
        if cal_dis<=given_dis:
            near_by.append(single_add)
    #check If there is no address under given distance 
    if len(near_by)==0:
            
        logger.error(f'No address within {distance_in_km}km radius range')
        # return that there are no address under given range to user  
        return f'No address within {distance_in_km}km radius range' 

    else:   

        logger.info(f'Nearest address in radius range {distance_in_km}km fetched successfully ')
        # return the nearby address data in the given range to user
        return near_by    

# Update the address
@app.put("/{address_id}")
def update_address(address_id:int, address:Address_Book, db: Session = Depends(get_db)):
    address_model = db.query(models.Address).filter(models.Address.id == address_id).first()

    # If data with that ID not found in database raise the status code and detail
    if address_model is None:

        logger.error(f"Address with ID {address_id} : Does not exist")
        raise HTTPException(
            status_code = 404,
            detail = f"Address with ID {address_id} : Does not exist"
        )

    # getting the location address for updating
    address_model.streetAddress = address.streetAddress
    address_model.city = address.city
    address_model.state = address.state
    address_model.country = address.country
    address_model.pincode = address.pincode
    # updating coordinate data from mapquest api in the coordinates.py file 
    full_add_data=coordinates.coordinates(f"{address_model.streetAddress},{address_model.city},{address_model.state}")
    logger.info(f"{full_add_data}")
    address_model.coordinates = f"{full_add_data[0]},{full_add_data[1]}"
    address_model.mapUrl = full_add_data[2]
    
    db.add(address_model)#adding to the database
    db.commit()# committing the changes to the database

    logger.info(f"Address with ID {address_id} updated")
    return address 


#Delete the address
@app.delete("/{address_id}")
def delete_address(address_id:int, db: Session = Depends(get_db)):
    
    address_model = db.query(models.Address).filter(models.Address.id == address_id).first()

    # If data with that ID not found in database raise the status code and detail
    if address_model is None:
        logger.error(f"Address with ID {address_id} : Does not exist")
        raise HTTPException(
            status_code=404,
            detail = f"Address with ID {address_id} : Does not exist"
        )
    #deleting the address of given ID
    db.query(models.Address).filter(models.Address.id == address_id).delete()
    db.commit() 
    logger.info(f"Address with ID {address_id} deleted")

    return f"Deleted address with ID:{address_id}"

    