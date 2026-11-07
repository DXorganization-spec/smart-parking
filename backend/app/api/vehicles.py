from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
from backend.app.services.rfid_service import identify_vehicle_by_rfid
from backend.app.database.connection import get_db
from backend.app.database.models import Vehicle
from backend.app.schemas.vehicle import (
    VehicleCreate,
    VehicleUpdate,
    VehicleResponse
)

router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"]
)


@router.post(
    "/",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED
)
def create_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db)
):
    vehicle = Vehicle(**vehicle_data.model_dump())

    db.add(vehicle)

    try:
        db.commit()
        db.refresh(vehicle)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="RFID UID or registration number already exists"
        )

    return vehicle


@router.get("/", response_model=list[VehicleResponse])
def get_vehicles(db: Session = Depends(get_db)):
    return db.query(Vehicle).all()


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    vehicle = db.get(Vehicle, vehicle_id)

    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return vehicle


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db)
):
    vehicle = db.get(Vehicle, vehicle_id)

    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    updates = vehicle_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    for field, value in updates.items():
        setattr(vehicle, field, value)

    try:
        db.commit()
        db.refresh(vehicle)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Vehicle update violates a database constraint"
        )

    return vehicle


@router.delete("/{vehicle_id}")
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    vehicle = db.get(Vehicle, vehicle_id)

    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    db.delete(vehicle)
    db.commit()

    return {"message": "Vehicle deleted successfully"}

class RFIDRequest(BaseModel):
    rfid_uid: str = Field(min_length=1, max_length=100)


@router.post("/identify-rfid")
def identify_rfid(
    request: RFIDRequest,
    db: Session = Depends(get_db)
):
    result = identify_vehicle_by_rfid(
        db,
        request.rfid_uid
    )

    if not result["success"]:
        raise HTTPException(
            status_code=404,
            detail=result["message"]
        )

    return result