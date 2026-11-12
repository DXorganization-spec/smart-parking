
from backend.app.services.vehicle_detection import detect_vehicles

image_path = "test_vehicle.jpg"

result = detect_vehicles(image_path)

print("\nYOLO VEHICLE DETECTION RESULT")
print("=" * 40)
print(result)
