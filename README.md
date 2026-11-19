# Smart Parking Management System

An AI-based Smart Parking Management and Dynamic Allocation System designed to improve parking-space utilization through vehicle detection, occupancy monitoring, and intelligent parking allocation.

## Project Overview

The Smart Parking Management System aims to simplify campus parking operations by combining computer vision, geospatial parking-zone management, and a backend allocation engine.

The system maintains parking zones and slots, monitors their occupancy status, manages vehicle records, and assigns available parking spaces to compatible vehicles.

## Technology Stack

| Component | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL, PostGIS |
| ORM | SQLAlchemy |
| Database Migrations | Alembic |
| API Server | Uvicorn |
| Data Validation | Pydantic |
| Computer Vision | OpenCV, YOLO |
| Configuration | Python dotenv |
| Version Control | Git, GitHub |

## Project Structure

```text
smart-parking/
|-- ai/
|-- backend/
|   |-- alembic/
|   |-- app/
|   |   |-- api/
|   |   |-- database/
|   |   |-- models/
|   |   |-- schemas/
|   |   |-- services/
|   |-- tests/
|   |-- requirements.txt
|-- data/
|-- docs/
|-- frontend/
|-- gis/
|-- rfid/
|-- scripts/
|-- tests/
|-- tools/
|-- .env.example
|-- alembic.ini
|-- annotate_zone_a.py
|-- README.md
```

## Implemented Backend Features

### 1. Vehicle Management

\- Vehicle registration and retrieval.

\- Vehicle information updates.

\- Vehicle identification through RFID-related API functionality.

### 2. Parking Zone and Slot Management

\- Parking-zone management.

\- Parking-slot management.

\- Vehicle-type compatibility.

\- Active and inactive parking resources.

### 3. Occupancy Management

\- Parking-slot occupancy status management.

\- Available, occupied, and unknown states.

\- Zone A occupancy detection endpoints.

### 4. Dynamic Parking Allocation

\- Compatible parking-slot selection.

\- Verification of slot availability before allocation.

\- Prevention of duplicate active vehicle allocations.

\- Transactional allocation and release operations.

\- Allocation history management.

### 5. Computer Vision and Vehicle Detection

\- Image-based vehicle detection.

\- Video-based vehicle detection.

\- Vehicle tracking endpoints.

\- Zone A image and video processing.

### 6. Analytics

\- Parking overview.

\- Zone-level analytics.

\- Allocation history and status information.

## Allocation and Concurrency Handling

The allocation engine uses SQLAlchemy transactions and PostgreSQL row-level locking.

Important allocation safeguards include:

\- Only verified available slots are eligible for allocation.

\- Unknown or occupied slots are not allocated.

\- Existing active allocations are checked before assigning another slot.

\- `FOR UPDATE SKIP LOCKED` helps prevent concurrent sessions from selecting the same locked slot.

\- Database uniqueness constraints protect active allocations per vehicle and per slot.

\- Releasing a reservation does not automatically change the physical occupancy state.

## Verified Allocation Checks

The following behaviours have been manually verified during development:

| Test | Result |
|---|---|
| Reject unknown parking slot | Passed |
| Allocate verified available slot | Passed |
| Reject duplicate vehicle allocation | Passed |
| Rollback restores database state | Passed |
| Release preserves physical occupancy | Passed |
| Two sessions competing for one slot | Passed |

The concurrency check used two independent database sessions competing for Zone A slot A01. One allocation succeeded while the other was rejected. Both transactions were rolled back, and the original slot state was restored.

These are development verification results, not automated CI test results.

## Installation and Setup

### Prerequisites

\- Python

\- PostgreSQL

\- PostGIS extension

\- Git

### 1. Clone the repository

```bash
git clone https://github.com/DXorganization-spec/smart-parking.git
cd smart-parking
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
```

### 3. Install backend dependencies

```powershell
pip install -r backend/requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using `.env.example` as a reference.

Set your own PostgreSQL connection string:

```env
DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/smart_parking
```

Do not commit `.env` or publish database credentials.

### 5. Start the backend

From the repository root:

```powershell
uvicorn backend.app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

FastAPI provides interactive API documentation.

\- Swagger UI: http://127.0.0.1:8000/docs

\- ReDoc: http://127.0.0.1:8000/redoc

\- Health endpoint: http://127.0.0.1:8000/health

The backend currently includes API modules for:

\- Vehicles

\- Parking zones and slots

\- Occupancy

\- Allocation

\- Analytics

\- Vehicle detection

## Current Development Status

The backend foundation, parking allocation engine, occupancy management, and Zone A detection workflows are under active development.

Current development priorities include:

\- Expanding automated backend tests.

\- Improving API validation and error handling.

\- Further testing vehicle detection and occupancy workflows.

\- Integrating and validating the remaining system modules.

\- Improving project documentation.

## Repository

GitHub: https://github.com/DXorganization-spec/smart-parking

\---

**Smart Parking Management System**

AI-based Parking Management | Dynamic Allocation | Computer Vision | Geospatial Technologies
