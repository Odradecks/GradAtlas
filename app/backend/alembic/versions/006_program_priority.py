"""add program ingestion priority

Revision ID: 006
Revises: 005
Create Date: 2026-09-29

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("programs", sa.Column("ingestion_priority", sa.String(length=8), nullable=True))


def downgrade() -> None:
    op.drop_column("programs", "ingestion_priority")
