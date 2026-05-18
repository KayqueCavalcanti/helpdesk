"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-17
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)
    op.create_index("ix_usuarios_id", "usuarios", ["id"], unique=False)

    op.create_table(
        "chamados",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("descricao", sa.String(length=2000), nullable=False),
        sa.Column("status", sa.Enum("Aberto", "Em Andamento", "Resolvido", name="statuschamado"), nullable=False),
        sa.Column("autor_id", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.ForeignKeyConstraint(["autor_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chamados_id", "chamados", ["id"], unique=False)

    op.create_table(
        "comentarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conteudo", sa.String(length=2000), nullable=False),
        sa.Column("chamado_id", sa.Integer(), nullable=False),
        sa.Column("autor_id", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.ForeignKeyConstraint(["autor_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chamado_id"], ["chamados.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comentarios_id", "comentarios", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_comentarios_id", table_name="comentarios")
    op.drop_table("comentarios")
    op.drop_index("ix_chamados_id", table_name="chamados")
    op.drop_table("chamados")
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_index("ix_usuarios_id", table_name="usuarios")
    op.drop_table("usuarios")
