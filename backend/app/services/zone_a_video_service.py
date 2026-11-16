
import cv2
from datetime import datetime, timezone

from backend.app.services.vehicle_detection import model
from backend.app.services.parking_roi_service import (
    ZONE_A_ID,
    CONFIDENCE_THRESHOLD,
    ZONE_A_ROIS,
    point_inside_roi,
)
from backend.app.database.models import ParkingSlot


REFERENCE_WIDTH = 1366
REFERENCE_HEIGHT = 768


def process_zone_a_video(
    db,
    video_path: str,
    slot_rois: dict = None,
    frame_interval: int = 10,
    min_detection_frames: int = 3,
):
    """Process video and update Zone A occupancy conservatively."""

    slot_rois = slot_rois if slot_rois is not None else ZONE_A_ROIS

    if frame_interval < 1 or min_detection_frames < 1:
        raise ValueError("Frame interval and minimum hits must be positive.")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("Could not open video.")

    frame_number = 0
    processed_frames = 0
    slot_hits = {slot: 0 for slot in slot_rois}

    try:
        while True:
            success, frame = cap.read()

            if not success:
                break

            frame_number += 1

            if frame_number % frame_interval != 0:
                continue

            height, width = frame.shape[:2]

            if width != REFERENCE_WIDTH or height != REFERENCE_HEIGHT:
                raise ValueError(
                    f"Video frame dimensions are {width}x{height}. "
                    f"Zone A ROIs require {REFERENCE_WIDTH}x{REFERENCE_HEIGHT}."
                )

            processed_frames += 1
            results = model(frame, verbose=False)

            # Count at most one detection hit per slot per frame.
            detected_in_frame = set()

            for result in results:
                for box in result.boxes:
                    if int(box.cls[0]) != 3:
                        continue

                    confidence = float(box.conf[0])

                    if confidence < CONFIDENCE_THRESHOLD:
                        continue

                    x1, y1, x2, y2 = box.xyxy[0].tolist()

                    if x2 <= x1 or y2 <= y1:
                        continue

                    center_x = (x1 + x2) / 2
                    bottom_y = y2

                    for slot_number, polygon in slot_rois.items():
                        if point_inside_roi(center_x, bottom_y, polygon):
                            detected_in_frame.add(slot_number)

            for slot_number in detected_in_frame:
                slot_hits[slot_number] += 1

    finally:
        cap.release()

    if processed_frames == 0:
        raise ValueError("No video frames were processed.")

    slots = (
        db.query(ParkingSlot)
        .filter(
            ParkingSlot.zone_id == ZONE_A_ID,
            ParkingSlot.vehicle_type == "motorcycle",
            ParkingSlot.is_active.is_(True),
        )
        .all()
    )

    updated_slots = []
    now = datetime.now(timezone.utc)

    for slot in slots:
        if slot.slot_number not in slot_rois:
            continue

        hits = slot_hits[slot.slot_number]
        is_occupied = hits >= min_detection_frames

        if is_occupied:
            slot.is_occupied = True
            slot.occupancy_status = "occupied"
            slot.last_detected_at = now
        else:
            # Insufficient detection is not proof of an empty space.
            slot.is_occupied = False
            slot.occupancy_status = "unknown"

        updated_slots.append({
            "slot_number": slot.slot_number,
            "is_occupied": slot.is_occupied,
            "occupancy_status": slot.occupancy_status,
            "detection_frames": hits,
            "last_detected_at": slot.last_detected_at,
        })

    db.commit()

    occupied_count = sum(
        item["occupancy_status"] == "occupied"
        for item in updated_slots
    )

    unknown_count = sum(
        item["occupancy_status"] == "unknown"
        for item in updated_slots
    )

    return {
        "success": True,
        "zone_id": ZONE_A_ID,
        "processed_frames": processed_frames,
        "occupied_slots": occupied_count,
        "unknown_slots": unknown_count,
        "available_slots": 0,
        "updated_slots": updated_slots,
    }
