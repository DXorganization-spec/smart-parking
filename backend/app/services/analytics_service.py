from sqlalchemy import func, case
from sqlalchemy.orm import Session

from backend.app.database.models import (
    ParkingSlot,
    ParkingZone,
    Vehicle,
    Allocation
)


def get_parking_analytics(db: Session):

    # Total active parking slots
    total_slots = (
        db.query(func.count(ParkingSlot.id))
        .filter(ParkingSlot.is_active.is_(True))
        .scalar() or 0
    )

    # Occupied active slots
    occupied_slots = (
        db.query(func.count(ParkingSlot.id))
        .filter(
            ParkingSlot.is_active.is_(True),
            ParkingSlot.is_occupied.is_(True)
        )
        .scalar() or 0
    )

    # Available slots
    available_slots = total_slots - occupied_slots

    # Occupancy percentage
    occupancy_rate = (
        round((occupied_slots / total_slots) * 100, 2)
        if total_slots > 0 else 0
    )

    # Active registered vehicles
    total_vehicles = (
        db.query(func.count(Vehicle.id))
        .filter(Vehicle.is_active.is_(True))
        .scalar() or 0
    )

    # Currently active allocations
    active_allocations = (
        db.query(func.count(Allocation.id))
        .filter(Allocation.status == "active")
        .scalar() or 0
    )

    return {
        "total_slots": total_slots,
        "occupied_slots": occupied_slots,
        "available_slots": available_slots,
        "occupancy_rate": occupancy_rate,
        "total_registered_vehicles": total_vehicles,
        "active_allocations": active_allocations
    }


def get_zone_analytics(db: Session):

    zones = db.query(ParkingZone).filter(
        ParkingZone.is_active.is_(True)
    ).all()

    results = []

    for zone in zones:

        total_slots = (
            db.query(func.count(ParkingSlot.id))
            .filter(
                ParkingSlot.zone_id == zone.id,
                ParkingSlot.is_active.is_(True)
            )
            .scalar() or 0
        )

        occupied_slots = (
            db.query(func.count(ParkingSlot.id))
            .filter(
                ParkingSlot.zone_id == zone.id,
                ParkingSlot.is_active.is_(True),
                ParkingSlot.is_occupied.is_(True)
            )
            .scalar() or 0
        )

        results.append({
            "zone_id": zone.id,
            "zone_name": zone.name,
            "zone_code": zone.code,
            "vehicle_type": zone.vehicle_type,
            "capacity": zone.capacity,
            "total_slots": total_slots,
            "occupied_slots": occupied_slots,
            "available_slots": total_slots - occupied_slots,
            "is_overflow": zone.is_overflow
        })

    return results