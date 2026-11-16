from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.schemas.allocation import AllocationRequest
from backend.app.services.allocation_engine import allocate_parking_slot
from backend.app.services.allocation_engine import release_parking_slot
from sqlalchemy.exc import IntegrityError

from backend.app.services.allocation_history_service import (
    get_allocation_history,
    get_active_allocations,
    get_released_allocations,
    get_vehicle_allocation_history
)

router = APIRouter(
    prefix="/allocation",
    tags=["Dynamic Parking Allocation"]
)



@router.post("/assign")
def assign_parking(
    request: AllocationRequest,
    db: Session = Depends(get_db)
):
    try:
        result = allocate_parking_slot(db, request.vehicle_id)

        if not result["success"]:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )

        db.commit()
        return result

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Concurrent allocation conflict. Please retry."
        )

    except Exception:
        db.rollback()
        raise


@router.post("/release/{vehicle_id}")
def release_parking(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = release_parking_slot(db, vehicle_id)

        if not result["success"]:
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail=result["message"]
            )

        db.commit()
        return result

    except Exception:
        db.rollback()
        raise

@router.get("/history")
def allocation_history(
    db: Session = Depends(get_db)
):
    return get_allocation_history(db)


@router.get("/active")
def active_allocations(
    db: Session = Depends(get_db)
):
    return get_active_allocations(db)


@router.get("/released")
def released_allocations(
    db: Session = Depends(get_db)
):
    return get_released_allocations(db)


@router.get("/vehicle/{vehicle_id}/history")
def vehicle_allocation_history(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    return get_vehicle_allocation_history(db, vehicle_id)