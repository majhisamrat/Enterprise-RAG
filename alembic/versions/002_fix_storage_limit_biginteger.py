"""Change storage_limit from Integer to BigInteger in organizations table.

Revision ID: 002
Revises: 001
Create Date: 2026-08-08 08:46:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Change storage_limit column type from INTEGER to BIGINT."""
    op.alter_column('organizations', 'storage_limit',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)


def downgrade() -> None:
    """Revert storage_limit column type from BIGINT to INTEGER."""
    op.alter_column('organizations', 'storage_limit',
                    existing_type=sa.BigInteger(),
                    type_=sa.Integer(),
                    existing_nullable=False)
