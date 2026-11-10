from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.database.models import (
    Allocation,
    Vehicle,
    ParkingSlot
)


def format_allocation(allocation, vehicle, slot):

    end_time = allocation.released_at or datetime.now(timezone.utc)

    duration = end_time - allocation.allocated_at

    return {
        "allocation_id": allocation.id,
        "vehicle_id": vehicle.id,
        "registration_number": vehicle.registration_number,
        "vehicle_type": vehicle.vehicle_type,
        "owner_name": vehicle.owner_name,
        "slot_id": slot.id,
        "slot_number": slot.slot_number,
        "zone_id": slot.zone_id,
        "allocated_at": allocation.allocated_at,
        "released_at": allocation.released_at,
        "status": allocation.status,
        "duration_seconds": int(duration.total_seconds())
    }


def get_allocation_history(db: Session):

    records = (
        db.query(Allocation, Vehicle, ParkingSlot)
        .join(Vehicle, Allocation.vehicle_id == Vehicle.id)
        .join(ParkingSlot, Allocation.slot_id == ParkingSlot.id)
        .order_by(Allocation.allocated_at.desc())
        .all()
    )

    return [
        format_allocation(allocation, vehicle, slot)
        for allocation, vehicle, slot in records
    ]


def get_active_allocations(db: Session):

    records = (
        db.query(Allocation, Vehicle, ParkingSlot)
        .join(Vehicle, Allocation.vehicle_id == Vehicle.id)
        .join(ParkingSlot, Allocation.slot_id == ParkingSlot.id)
        .filter(Allocation.status == "active")
        .order_by(Allocation.allocated_at.desc())
        .all()
    )

    return [
        format_allocation(allocation, vehicle, slot)
        for allocation, vehicle, slot in records
    ]


def get_released_allocations(db: Session):

    records = (
        db.query(Allocation, Vehicle, ParkingSlot)
        .join(Vehicle, Allocation.vehicle_id == Vehicle.id)
        .join(ParkingSlot, Allocation.slot_id == ParkingSlot.id)
        .filter(Allocation.status == "released")
        .order_by(Allocation.released_at.desc())
        .all()
    )

    return [
        format_allocation(allocation, vehicle, slot)
        for allocation, vehicle, slot in records
    ]


def get_vehicle_allocation_history(
    db: Session,
    vehicle_id: int
):

    records = (
        db.query(Allocation, Vehicle, ParkingSlot)
        .join(Vehicle, Allocation.vehicle_id == Vehicle.id)
        .join(ParkingSlot, Allocation.slot_id == ParkingSlot.id)
        .filter(Allocation.vehicle_id == vehicle_id)
        .order_by(Allocation.allocated_at.desc())
        .all()
    )

    return [
        format_allocation(allocation, vehicle, slot)
        for allocation, vehicle, slot in records
    ]