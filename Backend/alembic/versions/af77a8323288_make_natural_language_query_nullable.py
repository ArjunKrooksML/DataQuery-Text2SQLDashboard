"""make_natural_language_query_nullable

Revision ID: af77a8323288
Revises: 1ed7ff4e51c5
Create Date: 2025-08-11 16:19:15.205555

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af77a8323288'
down_revision: Union[str, None] = '1ed7ff4e51c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:


    op.alter_column('query_history', 'natural_language_query',
               existing_type=sa.TEXT(),
               nullable=True)



def downgrade() -> None:


    op.alter_column('query_history', 'natural_language_query',
               existing_type=sa.TEXT(),
               nullable=False)

