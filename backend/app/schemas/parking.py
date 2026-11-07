
from pydantic import BaseModel, ConfigDict, Field, field_validator


# -------------------------
# Parking Zone Schemas
# -------------------------

class ParkingZoneCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    code: str = Field(min_length=2, max_length=20)
    vehicle_type: str = Field(min_length=2, max_length=20)
    capacity: int = Field(ge=1)

    is_overflow: bool = False
    is_active: bool = True

    geometry_wkt: str = Field(
        description="Zone boundary as a POLYGON WKT geometry"
    )

    @field_validator("geometry_wkt")
    @classmethod
    def validate_polygon(cls, value):
        if not value.strip().upper().startswith("POLYGON"):
            raise ValueError("Geometry must be a POLYGON")
        return value


class ParkingZoneUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    code: str | None = Field(default=None, min_length=2, max_length=20)
    vehicle_type: str | None = Field(default=None, min_length=2, max_length=20)
    capacity: int | None = Field(default=None, ge=1)
    is_overflow: bool | None = None
    is_active: bool | None = None


class ParkingZoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    vehicle_type: str
    capacity: int
    is_overflow: bool
    is_active: bool


# -------------------------
# Parking Slot Schemas
# -------------------------

class ParkingSlotCreate(BaseModel):
    zone_id: int = Field(gt=0)
    slot_number: str = Field(min_length=1, max_length=20)
    vehicle_type: str = Field(min_length=2, max_length=20)

    is_occupied: bool = False
    is_active: bool = True

    geometry_wkt: str = Field(
        description="Slot location as a POINT WKT geometry"
    )

    @field_validator("geometry_wkt")
    @classmethod
    def validate_point(cls, value):
        if not value.strip().upper().startswith("POINT"):
            raise ValueError("Geometry must be a POINT")
        return value


class ParkingSlotUpdate(BaseModel):
    zone_id: int | None = Field(default=None, gt=0)
    slot_number: str | None = Field(default=None, min_length=1, max_length=20)
    vehicle_type: str | None = Field(default=None, min_length=2, max_length=20)
    is_occupied: bool | None = None
    is_active: bool | None = None


class ParkingSlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_id: int
    slot_number: str
    vehicle_type: str
    is_occupied: bool
    is_active: bool
