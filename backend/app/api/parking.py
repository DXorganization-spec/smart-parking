
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from geoalchemy2.elements import WKTElement

from backend.app.database.connection import get_db
from backend.app.database.models import ParkingZone, ParkingSlot
from backend.app.schemas.parking import (
    ParkingZoneCreate,
    ParkingZoneUpdate,
    ParkingZoneResponse,
    ParkingSlotCreate,
    ParkingSlotUpdate,
    ParkingSlotResponse
)

router = APIRouter(
    prefix="/parking",
    tags=["Parking"]
)


# =====================================
# PARKING ZONE APIs
# =====================================

@router.post(
    "/zones",
    response_model=ParkingZoneResponse,
    status_code=status.HTTP_201_CREATED
)
def create_parking_zone(
    zone_data: ParkingZoneCreate,
    db: Session = Depends(get_db)
):
    zone = ParkingZone(
        name=zone_data.name,
        code=zone_data.code,
        vehicle_type=zone_data.vehicle_type,
        capacity=zone_data.capacity,
        is_overflow=zone_data.is_overflow,
        is_active=zone_data.is_active,
        geometry=WKTElement(zone_data.geometry_wkt, srid=4326)
    )

    db.add(zone)

    try:
        db.commit()
        db.refresh(zone)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Parking zone code already exists or data violates a database constraint"
        )

    return zone


@router.get(
    "/zones",
    response_model=list[ParkingZoneResponse]
)
def get_parking_zones(db: Session = Depends(get_db)):
    return db.query(ParkingZone).all()


@router.get(
    "/zones/{zone_id}",
    response_model=ParkingZoneResponse
)
def get_parking_zone(
    zone_id: int,
    db: Session = Depends(get_db)
):
    zone = db.get(ParkingZone, zone_id)

    if zone is None:
        raise HTTPException(
            status_code=404,
            detail="Parking zone not found"
        )

    return zone


@router.patch(
    "/zones/{zone_id}",
    response_model=ParkingZoneResponse
)
def update_parking_zone(
    zone_id: int,
    zone_data: ParkingZoneUpdate,
    db: Session = Depends(get_db)
):
    zone = db.get(ParkingZone, zone_id)

    if zone is None:
        raise HTTPException(
            status_code=404,
            detail="Parking zone not found"
        )

    updates = zone_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    for field, value in updates.items():
        setattr(zone, field, value)

    try:
        db.commit()
        db.refresh(zone)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Update violates a database constraint"
        )

    return zone


@router.delete("/zones/{zone_id}")
def delete_parking_zone(
    zone_id: int,
    db: Session = Depends(get_db)
):
    zone = db.get(ParkingZone, zone_id)

    if zone is None:
        raise HTTPException(
            status_code=404,
            detail="Parking zone not found"
        )

    db.delete(zone)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete this zone because parking slots are associated with it"
        )

    return {"message": "Parking zone deleted successfully"}


# =====================================
# PARKING SLOT APIs
# =====================================

@router.post(
    "/slots",
    response_model=ParkingSlotResponse,
    status_code=status.HTTP_201_CREATED
)
def create_parking_slot(
    slot_data: ParkingSlotCreate,
    db: Session = Depends(get_db)
):
    zone = db.get(ParkingZone, slot_data.zone_id)

    if zone is None:
        raise HTTPException(
            status_code=404,
            detail="Parking zone not found"
        )

    slot = ParkingSlot(
        zone_id=slot_data.zone_id,
        slot_number=slot_data.slot_number,
        vehicle_type=slot_data.vehicle_type,
        is_occupied=slot_data.is_occupied,
        is_active=slot_data.is_active,
        geometry=WKTElement(slot_data.geometry_wkt, srid=4326)
    )

    db.add(slot)

    try:
        db.commit()
        db.refresh(slot)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Parking slot violates a database constraint"
        )

    return slot


@router.get(
    "/slots",
    response_model=list[ParkingSlotResponse]
)
def get_parking_slots(db: Session = Depends(get_db)):
    return db.query(ParkingSlot).all()


@router.get(
    "/slots/{slot_id}",
    response_model=ParkingSlotResponse
)
def get_parking_slot(
    slot_id: int,
    db: Session = Depends(get_db)
):
    slot = db.get(ParkingSlot, slot_id)

    if slot is None:
        raise HTTPException(
            status_code=404,
            detail="Parking slot not found"
        )

    return slot


@router.patch(
    "/slots/{slot_id}",
    response_model=ParkingSlotResponse
)
def update_parking_slot(
    slot_id: int,
    slot_data: ParkingSlotUpdate,
    db: Session = Depends(get_db)
):
    slot = db.get(ParkingSlot, slot_id)

    if slot is None:
        raise HTTPException(
            status_code=404,
            detail="Parking slot not found"
        )

    updates = slot_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if "zone_id" in updates:
        zone = db.get(ParkingZone, updates["zone_id"])

        if zone is None:
            raise HTTPException(
                status_code=404,
                detail="Parking zone not found"
            )

    for field, value in updates.items():
        setattr(slot, field, value)

    try:
        db.commit()
        db.refresh(slot)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Update violates a database constraint"
        )

    return slot


@router.delete("/slots/{slot_id}")
def delete_parking_slot(
    slot_id: int,
    db: Session = Depends(get_db)
):
    slot = db.get(ParkingSlot, slot_id)

    if slot is None:
        raise HTTPException(
            status_code=404,
            detail="Parking slot not found"
        )

    db.delete(slot)
    db.commit()

    return {"message": "Parking slot deleted successfully"}
