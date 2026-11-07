from sqlalchemy.orm import Session

from backend.app.database.models import Vehicle


def identify_vehicle_by_rfid(
    db: Session,
    rfid_uid: str
):
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.rfid_uid == rfid_uid)
        .first()
    )

    if vehicle is None:
        return {
            "success": False,
            "message": "RFID card is not registered"
        }

    if not vehicle.is_active:
        return {
            "success": False,
            "message": "Vehicle is inactive"
        }

    return {
        "success": True,
        "message": "Vehicle identified successfully",
        "vehicle": {
            "id": vehicle.id,
            "rfid_uid": vehicle.rfid_uid,
            "registration_number": vehicle.registration_number,
            "vehicle_type": vehicle.vehicle_type,
            "owner_name": vehicle.owner_name,
            "category": vehicle.category
        }
    }