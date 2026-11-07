from fastapi import FastAPI
from sqlalchemy import text

from backend.app.database.connection import engine
from backend.app.api.parking import router as parking_router
from backend.app.api.vehicles import router as vehicle_router

app = FastAPI(
    title="Smart Parking Management System",
    description="AI-based Smart Parking Management and Dynamic Allocation System",
    version="0.1.0"
)
app.include_router(parking_router)
app.include_router(vehicle_router)


@app.get("/")
def root():
    return {
        "project": "Smart Parking",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/database-test")
def database_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT current_database();"))
        database_name = result.scalar()

    return {
        "database": database_name,
        "status": "connected"
    }