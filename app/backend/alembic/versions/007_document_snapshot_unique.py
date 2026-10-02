"""One document row per parsed snapshot."""

from typing import Sequence, Union

from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_documents_source_snapshot",
        "documents",
        ["source_snapshot_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_documents_source_snapshot", "documents", type_="unique")
