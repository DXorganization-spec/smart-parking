import cv2
import json
import numpy as np

image = cv2.imread("zone_a_reference.jpg")
with open("zone_a_rois.json", "r") as f:
    data = json.load(f)

overlay = image.copy()

for name, points in data["slots"].items():
    polygon = np.array(points, dtype=np.int32)
    cv2.fillPoly(overlay, [polygon], (0, 255, 0))
    cv2.polylines(image, [polygon], True, (0, 255, 255), 2)
    x, y = points[0]
    cv2.putText(image, name, (x + 5, y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

image = cv2.addWeighted(overlay, 0.15, image, 0.85, 0)
cv2.imwrite("zone_a_roi_preview.jpg", image)
print("Preview saved: zone_a_roi_preview.jpg")
