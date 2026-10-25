"""add parking zones and slots

Revision ID: 814782b307e8
Revises: fd05d86cd396
Create Date: 2026-10-26

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2


revision: str = "814782b307e8"
down_revision: Union[str, Sequence[str], None] = "fd05d86cd396"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create parking zones and parking slots."""

    op.create_table(
        "parking_zones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("vehicle_type", sa.String(length=20), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("is_overflow", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "geometry",
            geoalchemy2.types.Geometry(
                geometry_type="POLYGON",
                srid=4326,
                dimension=2,
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_parking_zones_id",
        "parking_zones",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_parking_zones_code",
        "parking_zones",
        ["code"],
        unique=True,
    )

    op.create_table(
        "parking_slots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("zone_id", sa.Integer(), nullable=False),
        sa.Column("slot_number", sa.String(length=20), nullable=False),
        sa.Column("vehicle_type", sa.String(length=20), nullable=False),
        sa.Column("is_occupied", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "geometry",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                dimension=2,
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_parking_slots_id",
        "parking_slots",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_parking_slots_zone_id",
        "parking_slots",
        ["zone_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove parking slots and parking zones."""

    op.drop_index(
        "ix_parking_slots_zone_id",
        table_name="parking_slots",
    )

    op.drop_index(
        "ix_parking_slots_id",
        table_name="parking_slots",
    )

    op.drop_table("parking_slots")

    op.drop_index(
        "ix_parking_zones_code",
        table_name="parking_zones",
    )

    op.drop_index(
        "ix_parking_zones_id",
        table_name="parking_zones",
    )

    op.drop_table("parking_zones")