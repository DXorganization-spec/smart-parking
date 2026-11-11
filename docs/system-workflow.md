# Smart Parking System - Workflow

## Project Overview
An AI-driven dynamic parking allocation system designed for heterogeneous vehicles in constrained parking environments.

## System Workflow

1. Vehicle Arrival
   - A vehicle arrives at the parking entrance.
   - Its RFID tag is scanned.

2. Vehicle Identification
   - The system identifies the registered vehicle using its RFID UID.
   - Vehicle registration details and vehicle type are retrieved.

3. Dynamic Parking Allocation
   - The allocation engine identifies compatible available slots.
   - Allocation considers vehicle type, slot availability and parking constraints.
   - The selected slot is assigned to the vehicle.

4. Vehicle Detection
   - YOLO detects and classifies vehicles using camera footage.
   - Supported target classes include motorcycles, cars and buses.

5. Occupancy Monitoring
   - The system monitors parking slot occupancy.
   - Slot availability is updated based on vehicle movement and detection.

6. Parking Verification
   - The detected parking location is compared with the assigned slot.
   - Incorrect parking triggers a dashboard warning.

7. Dashboard
   - Displays the parking map, vehicle details, allocations, occupancy and alerts.

## Technology Stack

- Backend: Python, FastAPI
- Database: PostgreSQL, PostGIS
- Computer Vision: OpenCV, YOLO
- Geospatial Mapping: QGIS, GeoJSON, Leaflet
- Frontend: React, TypeScript
- Vehicle Identification: RFID

## Prototype Approach

The initial prototype will use a single college building parking area.
A top-down site image will be used to create its digital parking representation.

Recorded videos, simulated RFID scans and webcam streams can be used for demonstration before institutional hardware access is available.

Physical RFID reader integration and actual campus camera deployment are future integration tasks.
