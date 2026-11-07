from pydantic import BaseModel, ConfigDict, Field


class VehicleCreate(BaseModel):
    rfid_uid: str | None = None

    registration_number: str = Field(
        min_length=4,
        max_length=20
    )

    vehicle_type: str = Field(
        min_length=2,
        max_length=20
    )

    owner_name: str = Field(
        min_length=2,
        max_length=100
    )

    category: str = Field(
        min_length=2,
        max_length=20
    )

    is_active: bool = True


class VehicleUpdate(BaseModel):
    rfid_uid: str | None = None
    registration_number: str | None = Field(
        default=None, min_length=4, max_length=20
    )
    vehicle_type: str | None = Field(
        default=None, min_length=2, max_length=20
    )
    owner_name: str | None = Field(
        default=None, min_length=2, max_length=100
    )
    category: str | None = Field(
        default=None, min_length=2, max_length=20
    )
    is_active: bool | None = None


class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rfid_uid: str | None
    registration_number: str
    vehicle_type: str
    owner_name: str
    category: str
    is_active: bool