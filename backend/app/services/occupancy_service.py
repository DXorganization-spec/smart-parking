
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.database.models import ParkingSlot


VALID_OCCUPANCY_STATES = {
    "available",
    "occupied",
    "unknown",
}


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
    slot.occupancy_status = (
        "occupied" if is_occupied else "available"
    )
    slot.last_detected_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(slot)

    return {
        "success": True,
        "message": f"Parking slot is now {slot.occupancy_status}",
        "slot": {
            "id": slot.id,
            "zone_id": slot.zone_id,
            "slot_number": slot.slot_number,
            "vehicle_type": slot.vehicle_type,
            "is_occupied": slot.is_occupied,
            "occupancy_status": slot.occupancy_status,
            "last_detected_at": (
                slot.last_detected_at.isoformat()
                if slot.last_detected_at else None
            ),
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
        "occupancy_status": slot.occupancy_status,
        "last_detected_at": (
            slot.last_detected_at.isoformat()
            if slot.last_detected_at else None
        ),
        "is_active": slot.is_active,
        "status": slot.occupancy_status
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
            "occupancy_status": slot.occupancy_status,
            "last_detected_at": (
                slot.last_detected_at.isoformat()
                if slot.last_detected_at else None
            ),
            "is_active": slot.is_active,
            "status": slot.occupancy_status
        }
        for slot in slots
    ]
