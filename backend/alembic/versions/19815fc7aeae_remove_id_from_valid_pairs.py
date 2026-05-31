"""remove id from valid pairs

Revision ID: 19815fc7aeae
Revises: 088ace2fd457
Create Date: 2026-05-31 06:35:28.208210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '19815fc7aeae'
down_revision: Union[str, Sequence[str], None] = '088ace2fd457'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema to drop id and swap primary keys cleanly."""
    op.drop_constraint(
        'champion_item_valid_pairs_pkey', 
        'champion_item_valid_pairs', 
        type_='primary'
    )
    
    op.drop_column('champion_item_valid_pairs', 'id')
    
    op.create_primary_key(
        'champion_item_valid_pairs_pkey', 
        'champion_item_valid_pairs', 
        ['champion_id', 'item_id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'champion_item_valid_pairs_pkey', 
        'champion_item_valid_pairs', 
        type_='primary'
    )
    op.add_column(
        'champion_item_valid_pairs', 
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False, server_default="1")
    )
    op.alter_column("champion_item_valid_pairs", "id", server_default=None)
    
    op.create_primary_key(
        'champion_item_valid_pairs_pkey', 
        'champion_item_valid_pairs', 
        ['id']
    )