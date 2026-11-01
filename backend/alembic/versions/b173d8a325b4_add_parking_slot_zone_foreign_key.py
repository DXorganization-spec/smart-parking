
"""add parking slot zone foreign key

Revision ID: b173d8a325b4
Revises: 814782b307e8
"""

from typing import Sequence, Union

from alembic import op

revision: str = 'b173d8a325b4'
down_revision: Union[str, Sequence[str], None] = '814782b307e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_foreign_key(
        "fk_parking_slots_zone_id_parking_zones",
        "parking_slots",
        "parking_zones",
        ["zone_id"],
        ["id"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_parking_slots_zone_id_parking_zones",
        "parking_slots",
        type_="foreignkey"
    )
