
import math

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.services.parking_roi_service import (
    ZONE_A_ROIS,
    update_zone_a_occupancy,
)
from backend.app.services.occupancy_service import (
    update_slot_occupancy,
    get_slot_occupancy,
    get_all_occupancy,
)

router = APIRouter(
    prefix="/occupancy",
    tags=["Occupancy Management"]
)


@router.get("/")
def get_all_slots_occupancy(db: Session = Depends(get_db)):
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
    result = update_slot_occupancy(db, slot_id, is_occupied)

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

    if not isinstance(detections, list):
        raise HTTPException(
            status_code=400,
            detail="'detections' must be a list."
        )

    supplied_rois = payload.get("slot_rois")

    if supplied_rois is None:
        normalized_rois = ZONE_A_ROIS
    else:
        if not isinstance(supplied_rois, dict):
            raise HTTPException(
                status_code=400,
                detail="'slot_rois' must be an object."
            )

        normalized_rois = {}

        try:
            for slot_number, points in supplied_rois.items():
                if slot_number not in ZONE_A_ROIS:
                    raise ValueError(f"Unknown Zone A slot: {slot_number}")

                if not isinstance(points, list) or len(points) != 4:
                    raise ValueError(
                        f"{slot_number} must contain four corner points."
                    )

                polygon = []

                for point in points:
                    if not isinstance(point, (list, tuple)) or len(point) != 2:
                        raise ValueError(
                            f"Each {slot_number} point must contain [x, y]."
                        )

                    x, y = point

                    if (
                        isinstance(x, bool)
                        or isinstance(y, bool)
                        or not isinstance(x, (int, float))
                        or not isinstance(y, (int, float))
                        or not math.isfinite(x)
                        or not math.isfinite(y)
                    ):
                        raise ValueError(
                            f"{slot_number} contains invalid coordinates."
                        )

                    if not (0 <= x < 1366 and 0 <= y < 768):
                        raise ValueError(
                            f"{slot_number} coordinates exceed image bounds."
                        )

                    polygon.append([x, y])

                normalized_rois[slot_number] = polygon

        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    return update_zone_a_occupancy(
        db,
        detections,
        normalized_rois
    )
