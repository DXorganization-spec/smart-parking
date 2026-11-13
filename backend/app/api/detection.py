
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.services.vehicle_detection import detect_vehicles
from tempfile import NamedTemporaryFile
from backend.app.services.video_detection import detect_vehicles_in_video
from backend.app.services.vehicle_tracking import track_vehicles_in_video
from fastapi import Depends, Form
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.services.zone_a_video_service import process_zone_a_video

from backend.app.services.parking_roi_service import (
    ZONE_A_ROIS,
    update_zone_a_occupancy,
)

router = APIRouter(
    prefix="/detection",
    tags=["Vehicle Detection"]
)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@router.post("/image")
async def detect_vehicle_image(file: UploadFile = File(...)):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format. Upload JPG, JPEG, PNG, BMP or WEBP."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty."
        )

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Image size must not exceed 10 MB."
        )

    temp_path = None

    try:
        with NamedTemporaryFile(
            suffix=extension,
            delete=False
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        result = detect_vehicles(temp_path)

        return {
            "filename": file.filename,
            **result
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Vehicle detection failed: {str(exc)}"
        )

    finally:
        if temp_path and Path(temp_path).exists():
            Path(temp_path).unlink()

        await file.close()


@router.post("/video")
async def detect_vehicle_video(file: UploadFile = File(...)):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in {".mp4", ".avi", ".mov", ".mkv"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported video format. Upload MP4, AVI, MOV or MKV."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded video is empty."
        )

    if len(content) > 100 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Video size must not exceed 100 MB."
        )

    temp_path = None

    try:
        with NamedTemporaryFile(
            suffix=extension,
            delete=False
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        result = detect_vehicles_in_video(temp_path)

        return {
            "filename": file.filename,
            **result
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Video detection failed: {str(exc)}"
        )

    finally:
        if temp_path and Path(temp_path).exists():
            Path(temp_path).unlink()

        await file.close()



@router.post("/track-video")
async def track_vehicle_video(file: UploadFile = File(...)):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in {".mp4", ".avi", ".mov", ".mkv"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported video format."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded video is empty."
        )

    if len(content) > 100 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Video size must not exceed 100 MB."
        )

    temp_path = None

    try:
        with NamedTemporaryFile(
            suffix=extension,
            delete=False
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        result = track_vehicles_in_video(temp_path)

        return {
            "filename": file.filename,
            **result
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Vehicle tracking failed: {str(exc)}"
        )

    finally:
        if temp_path and Path(temp_path).exists():
            Path(temp_path).unlink()

        await file.close()
@router.post("/zone-a/video")
async def detect_zone_a_video(
    file: UploadFile = File(...),
    slot_rois: str = Form(...),
    db: Session = Depends(get_db)
):
    import json

    try:
        rois = json.loads(slot_rois)
        normalized_rois = {
            name: tuple(coords)
            for name, coords in rois.items()
        }

        for roi in normalized_rois.values():
            if len(roi) != 4:
                raise ValueError("Each ROI needs four coordinates.")

        suffix = Path(file.filename).suffix.lower()

        if suffix not in {".mp4", ".avi", ".mov", ".mkv"}:
            raise HTTPException(status_code=400, detail="Unsupported video format")

        with NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(await file.read())
            temp_path = temp.name

        try:
            return process_zone_a_video(
                db,
                temp_path,
                normalized_rois
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/zone-a/image")
async def detect_zone_a_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    suffix = Path(file.filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format"
        )

    with NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(await file.read())
        temp_path = temp.name

    try:
        result = detect_vehicles(temp_path)

        occupancy = update_zone_a_occupancy(
            db,
            result["detections"],
            ZONE_A_ROIS
        )

        return {
            "success": True,
            "detection": result,
            "occupancy": occupancy
        }
    finally:
        Path(temp_path).unlink(missing_ok=True)

