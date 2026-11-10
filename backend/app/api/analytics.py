from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.services.analytics_service import (
    get_parking_analytics,
    get_zone_analytics
)

router = APIRouter(
    prefix="/analytics",
    tags=["Parking Analytics"]
)


@router.get("/overview")
def parking_analytics(
    db: Session = Depends(get_db)
):
    return get_parking_analytics(db)


@router.get("/zones")
def zone_analytics(
    db: Session = Depends(get_db)
):
    return get_zone_analytics(db)