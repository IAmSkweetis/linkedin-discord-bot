"""f3b8b48

Revision ID: fbaf1f219406
Revises: 9e5bf78cb866
Create Date: 2025-04-23 18:15:58.230370

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "fbaf1f219406"
down_revision: Union[str, None] = "9e5bf78cb866"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "job",
        "job_id",
        existing_type=sa.INTEGER(),
        type_=sa.BIGINT(),
        existing_nullable=False,
        autoincrement=True,
    )
    op.alter_column(
        "jobquery",
        "creator_discord_id",
        existing_type=sa.INTEGER(),
        type_=sa.BIGINT(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "jobquery",
        "creator_discord_id",
        existing_type=sa.BIGINT(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
    op.alter_column(
        "job",
        "job_id",
        existing_type=sa.BIGINT(),
        type_=sa.INTEGER(),
        existing_nullable=False,
        autoincrement=True,
    )
    # ### end Alembic commands ###
