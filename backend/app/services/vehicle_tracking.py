
import cv2
from pathlib import Path

from backend.app.services.vehicle_detection import model, VEHICLE_CLASSES


def track_vehicles_in_video(video_path: str, frame_interval: int = 10):
    """
    Track vehicles across video frames using YOLO and ByteTrack.
    """

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        raise ValueError("Unable to open video file")

    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    video.release()

    detections = []
    tracked_vehicles = {}
    processed_frames = 0

    results = model.track(
        source=video_path,
        stream=True,
        tracker="bytetrack.yaml",
        vid_stride=frame_interval,
        persist=False,
        verbose=False
    )

    for frame_index, result in enumerate(results):
        processed_frames += 1

        frame_number = (frame_index * frame_interval) + 1

        timestamp = (
            round(frame_number / fps, 2)
            if fps and fps > 0 else 0
        )

        if result.boxes is None or result.boxes.id is None:
            continue

        track_ids = result.boxes.id.int().cpu().tolist()
        classes = result.boxes.cls.int().cpu().tolist()
        confidences = result.boxes.conf.cpu().tolist()
        coordinates = result.boxes.xyxy.cpu().tolist()

        for track_id, class_id, confidence, bbox in zip(
            track_ids, classes, confidences, coordinates
        ):
            if class_id not in VEHICLE_CLASSES:
                continue

            vehicle_type = VEHICLE_CLASSES[class_id]

            tracked_vehicles[track_id] = vehicle_type

            detections.append({
                "vehicle_id": track_id,
                "vehicle_type": vehicle_type,
                "frame_number": frame_number,
                "timestamp_seconds": timestamp,
                "confidence": round(float(confidence), 3),
                "bounding_box": [
                    round(float(value), 2) for value in bbox
                ]
            })

    vehicle_counts = {
        vehicle_type: sum(
            1 for detected_type in tracked_vehicles.values()
            if detected_type == vehicle_type
        )
        for vehicle_type in VEHICLE_CLASSES.values()
    }

    return {
        "success": True,
        "video_name": Path(video_path).name,
        "total_frames": total_frames,
        "processed_frames": processed_frames,
        "total_unique_vehicles": len(tracked_vehicles),
        "vehicle_counts": vehicle_counts,
        "detections": detections
    }
