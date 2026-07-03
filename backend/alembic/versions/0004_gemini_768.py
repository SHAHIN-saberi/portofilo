"""change embedding dimension to 768 for gemini text-embedding-004

Revision ID: 0004_gemini_768
Revises: 0003_fix_education_translations
Create Date: 2026-07-03 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "0004_gemini_768"
down_revision = "0003_fix_education_translations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing HNSW index on 1024-dim embedding
    op.drop_index("idx_knowledge_chunks_embedding", table_name="knowledge_chunks")
    # Truncate knowledge_chunks since 1024-dim vectors cannot be directly cast to 768-dim
    op.execute("TRUNCATE TABLE knowledge_chunks;")
    # Alter column embedding type from vector(1024) to vector(768)
    op.alter_column(
        "knowledge_chunks",
        "embedding",
        type_=Vector(768),
        existing_type=Vector(1024),
        nullable=False,
    )
    # Recreate HNSW index for 768-dim vector
    op.create_index(
        "idx_knowledge_chunks_embedding",
        "knowledge_chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index("idx_knowledge_chunks_embedding", table_name="knowledge_chunks")
    op.execute("TRUNCATE TABLE knowledge_chunks;")
    op.alter_column(
        "knowledge_chunks",
        "embedding",
        type_=Vector(1024),
        existing_type=Vector(768),
        nullable=False,
    )
    op.create_index(
        "idx_knowledge_chunks_embedding",
        "knowledge_chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
