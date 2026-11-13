
from sqlalchemy.orm import Session

from backend.app.database.models import ParkingSlot


ZONE_A_ID = 2
CONFIDENCE_THRESHOLD = 0.35
ZONE_A_ROIS = {
    "A01": (0, 0, 352, 192),
    "A02": (352, 0, 704, 192),
    "A03": (704, 0, 1056, 192),
    "A04": (1056, 0, 1408, 192),

    "A05": (0, 192, 352, 384),
    "A06": (352, 192, 704, 384),
    "A07": (704, 192, 1056, 384),
    "A08": (1056, 192, 1408, 384),

    "A09": (0, 384, 352, 576),
    "A10": (352, 384, 704, 576),
    "A11": (704, 384, 1056, 576),
    "A12": (1056, 384, 1408, 576),

    "A13": (0, 576, 352, 768),
    "A14": (352, 576, 704, 768),
    "A15": (704, 576, 1056, 768),
    "A16": (1056, 576, 1408, 768),
}


def point_inside_roi(x, y, roi):
    """
    Check whether a point is inside a parking-slot ROI.

    ROI format: (x1, y1, x2, y2)
    """
    x1, y1, x2, y2 = roi

    return x1 <= x <= x2 and y1 <= y <= y2


def update_zone_a_occupancy(db: Session, detections: list, slot_rois: dict):
    """
    Match motorcycle detections against Zone A parking-slot ROIs
    and update occupancy in the database.

    slot_rois example:
    {
        "A01": (100, 100, 200, 250),
        "A02": (210, 100, 310, 250)
    }
    """

    slots = (
        db.query(ParkingSlot)
        .filter(
            ParkingSlot.zone_id == ZONE_A_ID,
            ParkingSlot.vehicle_type == "motorcycle",
            ParkingSlot.is_active == True
        )
        .all()
    )

    detected_slots = set()

    for detection in detections:
        if detection.get("vehicle_type") != "motorcycle":
            continue

        confidence = detection.get("confidence", 0)

        if confidence < CONFIDENCE_THRESHOLD:
            continue

        bbox = detection.get("bounding_box")

        if not bbox or len(bbox) != 4:
            continue

        x1, y1, x2, y2 = bbox

        # Use the bottom-center of the bounding box
        # as an approximate vehicle-ground contact point.
        center_x = (x1 + x2) / 2
        bottom_y = y2

        for slot_number, roi in slot_rois.items():
            if point_inside_roi(center_x, bottom_y, roi):
                detected_slots.add(slot_number)

    updated_slots = []

    for slot in slots:
        if slot.slot_number not in slot_rois:
            continue

        slot.is_occupied = slot.slot_number in detected_slots

        updated_slots.append({
            "slot_id": slot.id,
            "slot_number": slot.slot_number,
            "is_occupied": slot.is_occupied,
            "status": "occupied" if slot.is_occupied else "available"
        })

    db.commit()

    return {
        "success": True,
        "zone_id": ZONE_A_ID,
        "vehicle_type": "motorcycle",
        "updated_slots": len(updated_slots),
        "occupied_slots": len(detected_slots),
        "available_slots": len(updated_slots) - len(detected_slots),
        "slots": updated_slots
    }
