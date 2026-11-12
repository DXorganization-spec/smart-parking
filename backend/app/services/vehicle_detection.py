
from ultralytics import YOLO

# Load pretrained YOLO model
model = YOLO("yolo11n.pt")

# COCO vehicle classes
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}


def detect_vehicles(image_path: str):
    """
    Detect vehicles in an image using YOLO.
    """

    results = model(image_path)

    detections = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])

            if class_id in VEHICLE_CLASSES:
                detections.append({
                    "vehicle_type": VEHICLE_CLASSES[class_id],
                    "confidence": round(float(box.conf[0]), 3),
                    "bounding_box": [
                        round(float(value), 2)
                        for value in box.xyxy[0].tolist()
                    ]
                })

    return {
        "success": True,
        "total_vehicles": len(detections),
        "detections": detections
    }
