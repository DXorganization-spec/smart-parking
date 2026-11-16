
import json
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from sqlalchemy.orm import Session

from backend.app.database.models import ParkingSlot


ZONE_A_ID = 2
CONFIDENCE_THRESHOLD = 0.35

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ROI_CONFIG_PATH = PROJECT_ROOT / "zone_a_rois.json"


def load_zone_a_rois():
    """Load and validate Zone A polygon coordinates."""

    if not ROI_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Zone A ROI configuration not found: {ROI_CONFIG_PATH}"
        )

    with ROI_CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = json.load(file)

    if config.get("image_width") != 1366 or config.get("image_height") != 768:
        raise ValueError("Unexpected Zone A reference image dimensions.")

    slots = config.get("slots", {})
    expected_slots = {f"A{i:02d}" for i in range(1, 17)}

    if set(slots) != expected_slots:
        raise ValueError("ROI configuration must contain exactly A01-A16.")

    validated = {}

    for name, points in slots.items():
        polygon = np.asarray(points, dtype=np.float32)

        if polygon.shape != (4, 2):
            raise ValueError(f"{name} must contain four 2D points.")

        if not np.isfinite(polygon).all():
            raise ValueError(f"{name} contains invalid coordinates.")

        if (
            (polygon[:, 0] < 0).any()
            or (polygon[:, 0] >= 1366).any()
            or (polygon[:, 1] < 0).any()
            or (polygon[:, 1] >= 768).any()
        ):
            raise ValueError(f"{name} contains out-of-image coordinates.")

        if abs(cv2.contourArea(polygon)) < 1:
            raise ValueError(f"{name} has an invalid polygon area.")

        validated[name] = polygon.astype(np.int32)

    return validated


ZONE_A_ROIS = load_zone_a_rois()


def point_inside_roi(x, y, roi):
    """Check whether a point is inside or on a polygon boundary."""

    polygon = np.asarray(roi, dtype=np.float32)

    return cv2.pointPolygonTest(
        polygon,
        (float(x), float(y)),
        False
    ) >= 0


def update_zone_a_occupancy(
    db: Session,
    detections: list,
    slot_rois: dict = None
):
    """
    Update Zone A occupancy using positive motorcycle detections.

    A positive detection confirms occupancy.
    A missing detection does not prove availability, so unmatched
    slots are marked unknown.
    """

    slot_rois = slot_rois if slot_rois is not None else ZONE_A_ROIS

    slots = (
        db.query(ParkingSlot)
        .filter(
            ParkingSlot.zone_id == ZONE_A_ID,
            ParkingSlot.vehicle_type == "motorcycle",
            ParkingSlot.is_active.is_(True)
        )
        .all()
    )

    detected_slots = set()

    for detection in detections:
        if detection.get("vehicle_type") != "motorcycle":
            continue

        try:
            confidence = float(detection.get("confidence", 0))
        except (TypeError, ValueError):
            continue

        if not np.isfinite(confidence) or confidence < CONFIDENCE_THRESHOLD:
            continue

        bbox = detection.get("bounding_box")

        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            continue

        try:
            x1, y1, x2, y2 = map(float, bbox)
        except (TypeError, ValueError):
            continue

        if not np.isfinite([x1, y1, x2, y2]).all():
            continue

        if x2 <= x1 or y2 <= y1:
            continue

        center_x = (x1 + x2) / 2
        bottom_y = y2

        for slot_number, polygon in slot_rois.items():
            if point_inside_roi(center_x, bottom_y, polygon):
                detected_slots.add(slot_number)

    updated_slots = []
    now = datetime.now(timezone.utc)

    for slot in slots:
        if slot.slot_number not in slot_rois:
            continue

        if slot.slot_number in detected_slots:
            slot.is_occupied = True
            slot.occupancy_status = "occupied"
            slot.last_detected_at = now
        else:
            slot.is_occupied = False
            slot.occupancy_status = "unknown"

        updated_slots.append({
            "slot_id": slot.id,
            "slot_number": slot.slot_number,
            "is_occupied": slot.is_occupied,
            "occupancy_status": slot.occupancy_status,
            "last_detected_at": slot.last_detected_at,
            "status": slot.occupancy_status
        })

    db.commit()

    occupied_count = sum(
        slot["occupancy_status"] == "occupied"
        for slot in updated_slots
    )

    unknown_count = sum(
        slot["occupancy_status"] == "unknown"
        for slot in updated_slots
    )

    return {
        "success": True,
        "zone_id": ZONE_A_ID,
        "vehicle_type": "motorcycle",
        "updated_slots": len(updated_slots),
        "occupied_slots": occupied_count,
        "unknown_slots": unknown_count,
        "available_slots": 0,
        "slots": updated_slots
    }
