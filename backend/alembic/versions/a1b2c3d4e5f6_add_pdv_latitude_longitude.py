"""add_pdv_latitude_longitude

Revision ID: a1b2c3d4e5f6
Revises: e713e26e2ee7
Create Date: 2026-02-18

Ajoute latitude et longitude (WGS84) aux points de vente pour affichage sur carte.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "e713e26e2ee7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "points_de_vente",
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
    )
    op.add_column(
        "points_de_vente",
        sa.Column("longitude", sa.Numeric(11, 7), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("points_de_vente", "longitude")
    op.drop_column("points_de_vente", "latitude")
