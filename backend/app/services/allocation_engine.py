
from datetime import datetime, timezone

from sqlalchemy import func, exists, select
from sqlalchemy.orm import Session

from backend.app.database.models import (
    Vehicle,
    ParkingZone,
    ParkingSlot,
    Allocation,
)


def allocate_parking_slot(db: Session, vehicle_id: int):
    """Reserve a verified available parking slot."""

    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == vehicle_id)
        .with_for_update()
        .first()
    )

    if vehicle is None:
        return {
            "success": False,
            "message": "Vehicle not found",
        }

    if not vehicle.is_active:
        return {
            "success": False,
            "message": "Vehicle is inactive",
        }

    existing = (
        db.query(Allocation)
        .filter(
            Allocation.vehicle_id == vehicle_id,
            Allocation.status == "active",
        )
        .first()
    )

    if existing:
        return {
            "success": False,
            "message": "Vehicle already has an active allocation",
        }

    active_reservation = exists(
        select(Allocation.id).where(
            Allocation.slot_id == ParkingSlot.id,
            Allocation.status == "active",
        )
    )

    slot = (
        db.query(ParkingSlot)
        .join(
            ParkingZone,
            ParkingSlot.zone_id == ParkingZone.id,
        )
        .filter(
            func.lower(ParkingSlot.vehicle_type)
            == vehicle.vehicle_type.lower(),
            func.lower(ParkingZone.vehicle_type)
            == vehicle.vehicle_type.lower(),
            ParkingSlot.occupancy_status == "available",
            ParkingSlot.is_occupied.is_(False),
            ParkingSlot.is_active.is_(True),
            ParkingZone.is_active.is_(True),
            ~active_reservation,
        )
        .order_by(
            ParkingZone.is_overflow.asc(),
            ParkingSlot.id.asc(),
        )
        .with_for_update(
            of=ParkingSlot,
            skip_locked=True,
        )
        .first()
    )

    if slot is None:
        return {
            "success": False,
            "message": "No verified compatible parking slot available",
        }

    allocation = Allocation(
        vehicle_id=vehicle.id,
        slot_id=slot.id,
        status="active",
    )

    db.add(allocation)
    db.flush()

    return {
        "success": True,
        "message": "Parking slot reserved successfully",
        "allocation": {
            "allocation_id": allocation.id,
            "vehicle_id": vehicle.id,
            "registration_number": vehicle.registration_number,
            "vehicle_type": vehicle.vehicle_type,
            "slot_id": slot.id,
            "slot_number": slot.slot_number,
            "zone_id": slot.zone_id,
            "occupancy_status": slot.occupancy_status,
            "status": allocation.status,
        },
    }


def release_parking_slot(db: Session, vehicle_id: int):
    """Release a reservation without changing physical occupancy."""

    allocation = (
        db.query(Allocation)
        .filter(
            Allocation.vehicle_id == vehicle_id,
            Allocation.status == "active",
        )
        .with_for_update()
        .first()
    )

    if allocation is None:
        return {
            "success": False,
            "message": "No active parking allocation found",
        }

    slot = db.get(ParkingSlot, allocation.slot_id)

    if slot is None:
        raise ValueError("Allocated parking slot not found")

    allocation.status = "released"
    allocation.released_at = datetime.now(timezone.utc)

    # Physical occupancy is not changed by reservation release.
    db.flush()

    return {
        "success": True,
        "message": "Parking reservation released successfully",
        "allocation": {
            "allocation_id": allocation.id,
            "vehicle_id": allocation.vehicle_id,
            "slot_id": slot.id,
            "slot_number": slot.slot_number,
            "occupancy_status": slot.occupancy_status,
            "status": allocation.status,
            "released_at": allocation.released_at.isoformat(),
        },
    }
