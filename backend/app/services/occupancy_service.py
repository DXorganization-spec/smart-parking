from sqlalchemy.orm import Session

from backend.app.database.models import ParkingSlot


def update_slot_occupancy(
    db: Session,
    slot_id: int,
    is_occupied: bool
):
    slot = db.get(ParkingSlot, slot_id)

    if slot is None:
        return None

    if not slot.is_active:
        return {
            "success": False,
            "message": "Parking slot is inactive"
        }

    slot.is_occupied = is_occupied

    db.commit()
    db.refresh(slot)

    return {
        "success": True,
        "message": (
            "Parking slot occupied successfully"
            if is_occupied
            else "Parking slot is now available"
        ),
        "slot": {
            "id": slot.id,
            "zone_id": slot.zone_id,
            "slot_number": slot.slot_number,
            "vehicle_type": slot.vehicle_type,
            "is_occupied": slot.is_occupied,
            "is_active": slot.is_active
        }
    }


def get_slot_occupancy(
    db: Session,
    slot_id: int
):
    slot = db.get(ParkingSlot, slot_id)

    if slot is None:
        return None

    return {
        "id": slot.id,
        "zone_id": slot.zone_id,
        "slot_number": slot.slot_number,
        "vehicle_type": slot.vehicle_type,
        "is_occupied": slot.is_occupied,
        "is_active": slot.is_active,
        "status": "occupied" if slot.is_occupied else "available"
    }


def get_all_occupancy(db: Session):
    slots = db.query(ParkingSlot).all()

    return [
        {
            "id": slot.id,
            "zone_id": slot.zone_id,
            "slot_number": slot.slot_number,
            "vehicle_type": slot.vehicle_type,
            "is_occupied": slot.is_occupied,
            "is_active": slot.is_active,
            "status": "occupied" if slot.is_occupied else "available"
        }
        for slot in slots
    ]