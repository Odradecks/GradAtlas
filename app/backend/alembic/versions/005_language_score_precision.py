"""widen language score columns for TOEFL iBT totals

Revision ID: 005
Revises: 004
Create Date: 2026-09-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_COLUMNS = (
    "minimum_overall",
    "minimum_reading",
    "minimum_writing",
    "minimum_listening",
    "minimum_speaking",
)


def upgrade() -> None:
    for col in _COLUMNS:
        op.alter_column(
            "language_requirements",
            col,
            existing_type=sa.Numeric(precision=3, scale=1),
            type_=sa.Numeric(precision=5, scale=1),
            existing_nullable=True,
        )


def downgrade() -> None:
    for col in _COLUMNS:
        op.alter_column(
            "language_requirements",
            col,
            existing_type=sa.Numeric(precision=5, scale=1),
            type_=sa.Numeric(precision=3, scale=1),
            existing_nullable=True,
        )
