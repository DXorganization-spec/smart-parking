
import cv2

from backend.app.services.vehicle_detection import model
from backend.app.services.parking_roi_service import (
    ZONE_A_ID,
    CONFIDENCE_THRESHOLD,
    point_inside_roi,
)
from backend.app.database.models import ParkingSlot


def process_zone_a_video(
    db,
    video_path: str,
    slot_rois: dict,
    frame_interval: int = 10,
    min_detection_frames: int = 3,
):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("Could not open video")

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

            processed_frames += 1
            results = model(frame, verbose=False)

            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])

                    # Zone A accepts motorcycles only.
                    if class_id != 3:
                        continue

                    confidence = float(box.conf[0])

                    if confidence < CONFIDENCE_THRESHOLD:
                        continue

                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    center_x = (x1 + x2) / 2
                    bottom_y = y2

                    for slot_number, roi in slot_rois.items():
                        if point_inside_roi(
                            center_x, bottom_y, roi
                        ):
                            slot_hits[slot_number] += 1

    finally:
        cap.release()

    if processed_frames == 0:
        raise ValueError("No video frames were processed")

    slots = (
        db.query(ParkingSlot)
        .filter(
            ParkingSlot.zone_id == ZONE_A_ID,
            ParkingSlot.vehicle_type == "motorcycle",
            ParkingSlot.is_active == True,
        )
        .all()
    )

    updated_slots = []

    for slot in slots:
        if slot.slot_number not in slot_rois:
            continue

        hits = slot_hits[slot.slot_number]
        is_occupied = hits >= min_detection_frames

        slot.is_occupied = is_occupied

        updated_slots.append({
            "slot_number": slot.slot_number,
            "is_occupied": is_occupied,
            "detection_frames": hits,
        })

    db.commit()

    return {
        "success": True,
        "zone_id": ZONE_A_ID,
        "processed_frames": processed_frames,
        "updated_slots": updated_slots,
    }
