from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from geopy.distance import geodesic
from pydantic import BaseModel
import models
from models import Address, SessionLocal

app = FastAPI()

class AddressCreate(BaseModel):
    street: str
    city: str
    state: str
    country: str
    latitude: float
    longitude: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/addresses/")
def create_address(address: AddressCreate, db: Session = Depends(get_db)):
    db_address = Address(
        street=address.street,
        city=address.city,
        state=address.state,
        country=address.country,
        latitude=address.latitude,
        longitude=address.longitude
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

@app.put("/addresses/{address_id}")
def update_address(address_id: int, address: AddressCreate, db: Session = Depends(get_db)):
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if db_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    db_address.street = address.street
    db_address.city = address.city
    db_address.state = address.state
    db_address.country = address.country
    db_address.latitude = address.latitude
    db_address.longitude = address.longitude
    db.commit()
    db.refresh(db_address)
    return db_address

@app.delete("/addresses/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db)):
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if db_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(db_address)
    db.commit()
    return {"ok": True}

@app.get("/addresses/")
def read_addresses(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    addresses = db.query(Address).offset(skip).limit(limit).all()
    return addresses

@app.get("/addresses/within_distance/")
def get_addresses_within_distance(latitude: float, longitude: float, distance: float, db: Session = Depends(get_db)):
    addresses = db.query(Address).all()
    origin = (latitude, longitude)
    nearby_addresses = []
    for address in addresses:
        addr_location = (address.latitude, address.longitude)
        if geodesic(origin, addr_location).km <= distance:
            nearby_addresses.append(address)
    return nearby_addresses
