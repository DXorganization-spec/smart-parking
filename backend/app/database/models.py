
from sqlalchemy import Boolean, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from backend.app.database.connection import Base
from sqlalchemy import (
    Boolean, Integer, String, ForeignKey,
    DateTime, func
)
from datetime import datetime

class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    rfid_uid: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True
    )

    registration_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )

    vehicle_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    owner_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )


class ParkingZone(Base):
    __tablename__ = "parking_zones"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )

    vehicle_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    capacity: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    is_overflow: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    geometry = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326),
        nullable=False
    )

    slots: Mapped[list["ParkingSlot"]] = relationship(
        back_populates="zone"
    )


class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    zone_id: Mapped[int] = mapped_column(
        ForeignKey("parking_zones.id"),
        nullable=False,
        index=True
    )

    slot_number: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    vehicle_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    is_occupied: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    geometry = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=False
    )

    zone: Mapped["ParkingZone"] = relationship(
        back_populates="slots"
    )

class Allocation(Base):
    __tablename__ = "allocations"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id"),
        nullable=False,
        index=True
    )

    slot_id: Mapped[int] = mapped_column(
        ForeignKey("parking_slots.id"),
        nullable=False,
        index=True
    )

    allocated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False
    )
