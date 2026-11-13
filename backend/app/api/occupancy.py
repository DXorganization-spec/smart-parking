from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend.app.services.parking_roi_service import update_zone_a_occupancy

from backend.app.database.connection import get_db
from backend.app.services.occupancy_service import (
    update_slot_occupancy,
    get_slot_occupancy,
    get_all_occupancy
)

router = APIRouter(
    prefix="/occupancy",
    tags=["Occupancy Management"]
)


@router.get("/")
def get_all_slots_occupancy(
    db: Session = Depends(get_db)
):
    return get_all_occupancy(db)


@router.get("/{slot_id}")
def get_single_slot_occupancy(
    slot_id: int,
    db: Session = Depends(get_db)
):
    result = get_slot_occupancy(db, slot_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Parking slot not found"
        )

    return result


@router.patch("/{slot_id}")
def update_occupancy(
    slot_id: int,
    is_occupied: bool,
    db: Session = Depends(get_db)
):
    result = update_slot_occupancy(
        db,
        slot_id,
        is_occupied
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Parking slot not found"
        )

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    return result


@router.post("/zone-a/detect")
def detect_zone_a_occupancy(
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):
    detections = payload.get("detections")
    slot_rois = payload.get("slot_rois")

    if not isinstance(detections, list) or not isinstance(slot_rois, dict):
        raise HTTPException(
            status_code=400,
            detail="Provide detections as a list and slot_rois as an object."
        )

    try:
        normalized_rois = {
            slot_number: tuple(roi)
            for slot_number, roi in slot_rois.items()
        }

        for roi in normalized_rois.values():
            if len(roi) != 4:
                raise ValueError("Each ROI must contain four coordinates.")

        return update_zone_a_occupancy(
            db,
            detections,
            normalized_rois
        )

    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
