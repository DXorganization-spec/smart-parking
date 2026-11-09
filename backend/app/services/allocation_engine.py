from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from backend.app.database.models import (
    Vehicle,
    ParkingZone,
    ParkingSlot,
    Allocation
)


def allocate_parking_slot(db: Session, vehicle_id: int):

    try:
        # 1. Find registered vehicle
        vehicle = db.get(Vehicle, vehicle_id)

        if vehicle is None:
            return {
                "success": False,
                "message": "Vehicle not found"
            }

        if not vehicle.is_active:
            return {
                "success": False,
                "message": "Vehicle is inactive"
            }

        # 2. Check existing active allocation
        existing = db.query(Allocation).filter(
            Allocation.vehicle_id == vehicle_id,
            Allocation.status == "active"
        ).first()

        if existing:
            return {
                "success": False,
                "message": "Vehicle already has an active allocation"
            }

        # 3. Find compatible available parking slot
        slot = (
            db.query(ParkingSlot)
            .join(
                ParkingZone,
                ParkingSlot.zone_id == ParkingZone.id
            )
            .filter(
                func.lower(ParkingSlot.vehicle_type)
                == vehicle.vehicle_type.lower(),
                func.lower(ParkingZone.vehicle_type)
                == vehicle.vehicle_type.lower(),
                ParkingSlot.is_occupied == False,
                ParkingSlot.is_active == True,
                ParkingZone.is_active == True
            )
            .order_by(
                ParkingZone.is_overflow.asc(),
                ParkingSlot.id.asc()
            )
            .with_for_update(
                of=ParkingSlot,
                skip_locked=True
            )
            .first()
        )

        if slot is None:
            db.rollback()
            return {
                "success": False,
                "message": "No compatible parking slot available"
            }

        # 4. Create allocation record
        allocation = Allocation(
            vehicle_id=vehicle.id,
            slot_id=slot.id,
            status="active"
        )

        # 5. Mark parking slot as occupied
        slot.is_occupied = True

        db.add(allocation)
        db.commit()

        db.refresh(allocation)
        db.refresh(slot)

        return {
            "success": True,
            "message": "Parking slot allocated successfully",
            "allocation": {
                "allocation_id": allocation.id,
                "vehicle_id": vehicle.id,
                "registration_number": vehicle.registration_number,
                "vehicle_type": vehicle.vehicle_type,
                "slot_id": slot.id,
                "slot_number": slot.slot_number,
                "zone_id": slot.zone_id,
                "status": allocation.status
            }
        }

    except Exception:
        db.rollback()
        raise



def release_parking_slot(db: Session, vehicle_id: int):

    try:
        allocation = (
            db.query(Allocation)
            .filter(
                Allocation.vehicle_id == vehicle_id,
                Allocation.status == "active"
            )
            .with_for_update()
            .first()
        )

        if allocation is None:
            return {
                "success": False,
                "message": "No active parking allocation found"
            }

        slot = db.get(ParkingSlot, allocation.slot_id)

        if slot is None:
            raise ValueError("Allocated parking slot not found")

        allocation.status = "released"
        allocation.released_at = datetime.now(timezone.utc)
        slot.is_occupied = False

        db.commit()
        db.refresh(allocation)
        db.refresh(slot)

        return {
            "success": True,
            "message": "Parking slot released successfully",
            "allocation": {
                "allocation_id": allocation.id,
                "vehicle_id": allocation.vehicle_id,
                "slot_id": slot.id,
                "slot_number": slot.slot_number,
                "status": allocation.status,
                "released_at": allocation.released_at.isoformat()
            }
        }

    except Exception:
        db.rollback()
        raise