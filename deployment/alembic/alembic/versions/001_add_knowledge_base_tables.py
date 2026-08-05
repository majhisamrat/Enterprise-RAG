"""Add Knowledge Base tables for Embedding Knowledge Platform.

Revision ID: 001
Revises: 
Create Date: 2026-07-29 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create new Knowledge Base tables."""
    
    # 1. Create knowledge_bases table
    op.create_table(
        'knowledge_bases',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('organization_id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('query_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_queried_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_knowledge_bases_organization_id', 'knowledge_bases', ['organization_id'])
    op.create_index('ix_knowledge_bases_status', 'knowledge_bases', ['status'])

    # 2. Create uploads table
    op.create_table(
        'uploads',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('knowledge_base_id', postgresql.UUID(), nullable=False),
        sa.Column('organization_id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=True),
        sa.Column('file_type', sa.String(20), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('storage_path', sa.Text(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('chunk_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('embedding_model', sa.String(255), nullable=False, server_default='BAAI/bge-small-en-v1.5'),
        sa.Column('embedding_dimension', sa.Integer(), nullable=False, server_default='384'),
        sa.Column('total_vectors', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('processing_status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('processing_start_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_end_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_duration_ms', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('vector_collection_name', sa.String(255), nullable=True),
        sa.Column('qdrant_index_name', sa.String(255), nullable=True),
        sa.Column('elasticsearch_index_name', sa.String(255), nullable=True),
        sa.Column('tags', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['knowledge_base_id'], ['knowledge_bases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_uploads_knowledge_base_id', 'uploads', ['knowledge_base_id'])
    op.create_index('ix_uploads_processing_status', 'uploads', ['processing_status'])
    op.create_index('ix_uploads_created_at', 'uploads', ['created_at'])

    # 3. Create embedding_collections table
    op.create_table(
        'embedding_collections',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('upload_id', postgresql.UUID(), nullable=False),
        sa.Column('knowledge_base_id', postgresql.UUID(), nullable=False),
        sa.Column('collection_name', sa.String(255), nullable=False),
        sa.Column('index_name', sa.String(255), nullable=True),
        sa.Column('vector_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['upload_id'], ['uploads.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['knowledge_base_id'], ['knowledge_bases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('upload_id')
    )
    op.create_index('ix_embedding_collections_upload_id', 'embedding_collections', ['upload_id'])

    # 4. Create query_logs table
    op.create_table(
        'query_logs',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('organization_id', postgresql.UUID(), nullable=False),
        sa.Column('knowledge_base_id', postgresql.UUID(), nullable=True),
        sa.Column('upload_id', postgresql.UUID(), nullable=True),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('retrieved_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('latency_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('used_upload_ids', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['knowledge_base_id'], ['knowledge_bases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['upload_id'], ['uploads.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_query_logs_user_id', 'query_logs', ['user_id'])
    op.create_index('ix_query_logs_organization_id', 'query_logs', ['organization_id'])
    op.create_index('ix_query_logs_knowledge_base_id', 'query_logs', ['knowledge_base_id'])
    op.create_index('ix_query_logs_created_at', 'query_logs', ['created_at'])

    # 5. Create vector_metadata table (denormalized cache for dashboard)
    op.create_table(
        'vector_metadata',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('knowledge_base_id', postgresql.UUID(), nullable=False),
        sa.Column('upload_id', postgresql.UUID(), nullable=False),
        sa.Column('organization_id', postgresql.UUID(), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('chunk_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_vectors', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('embedding_model', sa.String(255), nullable=False),
        sa.Column('query_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_queried_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['knowledge_base_id'], ['knowledge_bases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['upload_id'], ['uploads.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vector_metadata_knowledge_base_id', 'vector_metadata', ['knowledge_base_id'])
    op.create_index('ix_vector_metadata_upload_id', 'vector_metadata', ['upload_id'])

    # 6. Add knowledge_base_id column to chat_sessions table
    op.add_column(
        'chat_sessions',
        sa.Column('knowledge_base_id', postgresql.UUID(), nullable=True)
    )
    op.create_foreign_key(
        'fk_chat_sessions_knowledge_base_id',
        'chat_sessions', 'knowledge_bases',
        ['knowledge_base_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_index('ix_chat_sessions_knowledge_base_id', 'chat_sessions', ['knowledge_base_id'])


def downgrade() -> None:
    """Rollback Knowledge Base tables."""
    
    # Remove FK and column from chat_sessions
    op.drop_index('ix_chat_sessions_knowledge_base_id', table_name='chat_sessions')
    op.drop_constraint('fk_chat_sessions_knowledge_base_id', 'chat_sessions', type_='foreignkey')
    op.drop_column('chat_sessions', 'knowledge_base_id')

    # Drop vector_metadata table
    op.drop_index('ix_vector_metadata_upload_id', table_name='vector_metadata')
    op.drop_index('ix_vector_metadata_knowledge_base_id', table_name='vector_metadata')
    op.drop_table('vector_metadata')

    # Drop query_logs table
    op.drop_index('ix_query_logs_created_at', table_name='query_logs')
    op.drop_index('ix_query_logs_knowledge_base_id', table_name='query_logs')
    op.drop_index('ix_query_logs_organization_id', table_name='query_logs')
    op.drop_index('ix_query_logs_user_id', table_name='query_logs')
    op.drop_table('query_logs')

    # Drop embedding_collections table
    op.drop_index('ix_embedding_collections_upload_id', table_name='embedding_collections')
    op.drop_table('embedding_collections')

    # Drop uploads table
    op.drop_index('ix_uploads_created_at', table_name='uploads')
    op.drop_index('ix_uploads_processing_status', table_name='uploads')
    op.drop_index('ix_uploads_knowledge_base_id', table_name='uploads')
    op.drop_table('uploads')

    # Drop knowledge_bases table
    op.drop_index('ix_knowledge_bases_status', table_name='knowledge_bases')
    op.drop_index('ix_knowledge_bases_organization_id', table_name='knowledge_bases')
    op.drop_table('knowledge_bases')
