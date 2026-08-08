"""Create core tables: organizations, roles, permissions, users, user_sessions.

Revision ID: 000
Revises: 
Create Date: 2026-08-08 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create core database tables."""
    
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('subscription_plan', sa.String(50), nullable=False, server_default='enterprise'),
        sa.Column('storage_limit', sa.BigInteger(), nullable=False, server_default='107374182400'),  # 100GB
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('domain')
    )
    op.create_index('ix_organizations_domain', 'organizations', ['domain'])

    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('resource', sa.String(50), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create role_permissions join table
    op.create_table(
        'role_permissions',
        sa.Column('role_id', postgresql.UUID(), nullable=False),
        sa.Column('permission_id', postgresql.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('organization_id', postgresql.UUID(), nullable=False),
        sa.Column('role_id', postgresql.UUID(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('auth_provider', sa.String(50), nullable=False, server_default='local'),
        sa.Column('google_sub', sa.String(255), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=False),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('designation', sa.String(100), nullable=True),
        sa.Column('avatar', sa.String(500), nullable=True),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='UTC'),
        sa.Column('language', sa.String(10), nullable=False, server_default='en'),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_sub')
    )
    op.create_index('ix_users_organization_id', 'users', ['organization_id'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_google_sub', 'users', ['google_sub'])
    op.create_index('ix_users_department', 'users', ['department'])

    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('refresh_token')
    )
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'])


def downgrade() -> None:
    """Drop core tables."""
    op.drop_table('user_sessions')
    op.drop_table('users')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('organizations')
