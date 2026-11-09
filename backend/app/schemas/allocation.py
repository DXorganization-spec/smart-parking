from pydantic import BaseModel, Field


class AllocationRequest(BaseModel):
    vehicle_id: int = Field(
        gt=0,
        description="ID of the registered vehicle"
    )