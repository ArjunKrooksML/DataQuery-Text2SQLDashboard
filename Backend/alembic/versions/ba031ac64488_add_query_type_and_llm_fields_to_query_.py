"""Add query_type and LLM fields to query_history

Revision ID: ba031ac64488
Revises: af77a8323288
Create Date: 2025-08-14 14:36:59.348814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba031ac64488'
down_revision: Union[str, None] = 'af77a8323288'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the enum type if it doesn't exist
    op.execute("DO $$ BEGIN CREATE TYPE querytype AS ENUM ('SQL', 'LLM'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    
    # Add query_type column as nullable first
    op.add_column('query_history', sa.Column('query_type', sa.Enum('SQL', 'LLM', name='querytype'), nullable=True))
    
    # Update existing records to have SQL as default query_type
    op.execute("UPDATE query_history SET query_type = 'SQL' WHERE query_type IS NULL")
    
    # Now make the column NOT NULL
    op.alter_column('query_history', 'query_type', nullable=False)
    
    # Add other columns
    op.add_column('query_history', sa.Column('llm_response', sa.Text(), nullable=True))
    op.add_column('query_history', sa.Column('confidence_score', sa.Integer(), nullable=True))
    op.alter_column('query_history', 'generated_sql_query',
               existing_type=sa.TEXT(),
               nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('query_history', 'generated_sql_query',
               existing_type=sa.TEXT(),
               nullable=False)
    op.drop_column('query_history', 'confidence_score')
    op.drop_column('query_history', 'llm_response')
    op.drop_column('query_history', 'query_type')
    op.execute("DROP TYPE querytype")
