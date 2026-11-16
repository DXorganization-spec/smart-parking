
import cv2
import json
from pathlib import Path
import numpy as np

IMAGE_PATH = "zone_a_reference.jpg"
OUTPUT_PATH = "zone_a_rois.json"

image = cv2.imread(IMAGE_PATH)

if image is None:
    raise FileNotFoundError(f"Cannot find {IMAGE_PATH}")

height, width = image.shape[:2]

slot_names = (
    [f"A{i:02d}" for i in range(1, 9)]
    + [f"A{i:02d}" for i in range(9, 17)]
)

rois = {}
current_points = []
current_slot = 0
window = "Zone A ROI Annotation"

def draw():
    display = image.copy()

    for name, points in rois.items():
        polygon = np.array(points, dtype=np.int32)
        cv2.polylines(display, [polygon], True, (0, 255, 0), 3)

        center = np.mean(polygon, axis=0).astype(int)
        cv2.putText(
            display, name, tuple(center),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
            (0, 0, 255), 2
        )

    if current_points:
        for point in current_points:
            cv2.circle(display, point, 5, (255, 0, 0), -1)

        if len(current_points) > 1:
            cv2.polylines(
                display,
                [np.array(current_points, dtype=np.int32)],
                False, (255, 0, 0), 2
            )

    if current_slot < 16:
        instruction = (
            f"Slot: {slot_names[current_slot]} | "
            f"Click corner {len(current_points)+1}/4"
        )
    else:
        instruction = "All 16 ROIs marked. Press S to save."

    cv2.putText(
        display, instruction, (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8,
        (0, 0, 255), 2
    )

    cv2.imshow(window, display)


def mouse_callback(event, x, y, flags, param):
    global current_points, current_slot

    if event != cv2.EVENT_LBUTTONDOWN:
        return

    if current_slot >= 16:
        return

    current_points.append((x, y))

    if len(current_points) == 4:
        rois[slot_names[current_slot]] = current_points.copy()
        current_points.clear()
        current_slot += 1

    draw()


cv2.namedWindow(window, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window, width, height)
cv2.setMouseCallback(window, mouse_callback)

draw()

print("Select four corners for each parking space.")
print("Order: top-left, top-right, bottom-right, bottom-left.")
print("U = undo last slot | R = reset current slot")
print("S = save after all 16 slots | ESC = exit without saving")

while True:
    key = cv2.waitKey(0) & 0xFF

    if key == ord("u") and current_slot > 0:
        current_slot -= 1
        rois.pop(slot_names[current_slot], None)
        current_points.clear()
        draw()

    elif key == ord("r"):
        current_points.clear()
        draw()

    elif key == ord("s"):
        if current_slot != 16:
            print(f"Only {current_slot}/16 slots marked.")
            continue

        with open(OUTPUT_PATH, "w") as file:
            json.dump(
                {
                    "image_width": width,
                    "image_height": height,
                    "slots": rois
                },
                file,
                indent=4
            )

        print(f"Saved {len(rois)} ROIs to {OUTPUT_PATH}")
        break

    elif key == 27:
        print("Annotation cancelled. Nothing saved.")
        break

cv2.destroyAllWindows()
