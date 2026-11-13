
import cv2
from pathlib import Path

from backend.app.services.vehicle_detection import model, VEHICLE_CLASSES


def detect_vehicles_in_video(video_path: str, frame_interval: int = 10):
    """
    Process a video frame by frame and detect vehicles using YOLO.

    frame_interval=10 means process every 10th frame.
    """

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        raise ValueError("Unable to open video file")

    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_number = 0
    processed_frames = 0
    detections = []

    try:
        while True:
            success, frame = video.read()

            if not success:
                break

            frame_number += 1

            if frame_number % frame_interval != 0:
                continue

            results = model(frame, verbose=False)
            processed_frames += 1

            timestamp = round(
                frame_number / fps, 2
            ) if fps and fps > 0 else 0

            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])

                    if class_id not in VEHICLE_CLASSES:
                        continue

                    detections.append({
                        "frame_number": frame_number,
                        "timestamp_seconds": timestamp,
                        "vehicle_type": VEHICLE_CLASSES[class_id],
                        "confidence": round(float(box.conf[0]), 3),
                        "bounding_box": [
                            round(float(value), 2)
                            for value in box.xyxy[0].tolist()
                        ]
                    })

    finally:
        video.release()

    counts = {
        vehicle_type: sum(
            1 for detection in detections
            if detection["vehicle_type"] == vehicle_type
        )
        for vehicle_type in VEHICLE_CLASSES.values()
    }

    return {
        "success": True,
        "video_name": Path(video_path).name,
        "total_frames": total_frames,
        "processed_frames": processed_frames,
        "total_detections": len(detections),
        "vehicle_counts": counts,
        "detections": detections
    }
