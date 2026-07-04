"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-06-27

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema with all tables."""
    # Create clientes table
    op.create_table(
        "clientes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("cpf_cnpj", sa.String(14), unique=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("telefone", sa.String(20), nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("idx_clientes_cpf_cnpj", "clientes", ["cpf_cnpj"])

    # Create veiculos table
    op.create_table(
        "veiculos",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "cliente_id", sa.String(36), sa.ForeignKey("clientes.id"), nullable=False
        ),
        sa.Column("placa", sa.String(10), unique=True, nullable=False),
        sa.Column("marca", sa.String(100), nullable=False),
        sa.Column("modelo", sa.String(100), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("idx_veiculos_cliente_id", "veiculos", ["cliente_id"])
    op.create_index("idx_veiculos_placa", "veiculos", ["placa"])

    # Create servicos table
    op.create_table(
        "servicos",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("descricao", sa.String(500), server_default=""),
        sa.Column("preco_base", sa.Numeric(10, 2), nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(), server_default=sa.func.now()),
    )

    # Create pecas table
    op.create_table(
        "pecas",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("sku", sa.String(50), unique=True, nullable=False),
        sa.Column("preco", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantidade_estoque", sa.Integer(), server_default=sa.text("0")),
        sa.Column("estoque_minimo", sa.Integer(), server_default=sa.text("0")),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("idx_pecas_sku", "pecas", ["sku"])

    # Create ordens_servico table
    op.create_table(
        "ordens_servico",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "cliente_id", sa.String(36), sa.ForeignKey("clientes.id"), nullable=False
        ),
        sa.Column(
            "veiculo_id", sa.String(36), sa.ForeignKey("veiculos.id"), nullable=False
        ),
        sa.Column("status", sa.String(30), server_default="RECEBIDA"),
        sa.Column("orcamento_aprovado", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("orcamento_recusado", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("observacoes", sa.String(500), server_default=""),
        sa.Column("deletada", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("criada_em", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("atualizada_em", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("finalizada_em", sa.DateTime(), nullable=True),
        sa.Column("entregue_em", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_ordens_servico_cliente_id", "ordens_servico", ["cliente_id"])
    op.create_index("idx_ordens_servico_veiculo_id", "ordens_servico", ["veiculo_id"])

    # Create itens_servico table
    op.create_table(
        "itens_servico",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "ordem_servico_id",
            sa.String(36),
            sa.ForeignKey("ordens_servico.id"),
            nullable=False,
        ),
        sa.Column("servico_id", sa.String(36), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("preco", sa.Numeric(10, 2), nullable=False),
    )
    op.create_index(
        "idx_itens_servico_ordem_servico_id", "itens_servico", ["ordem_servico_id"]
    )

    # Create itens_peca table
    op.create_table(
        "itens_peca",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "ordem_servico_id",
            sa.String(36),
            sa.ForeignKey("ordens_servico.id"),
            nullable=False,
        ),
        sa.Column("peca_id", sa.String(36), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("preco_unitario", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
    )
    op.create_index(
        "idx_itens_peca_ordem_servico_id", "itens_peca", ["ordem_servico_id"]
    )


def downgrade() -> None:
    """Drop all tables in reverse order."""
    op.drop_table("itens_peca")
    op.drop_table("itens_servico")
    op.drop_table("ordens_servico")
    op.drop_table("pecas")
    op.drop_table("servicos")
    op.drop_table("veiculos")
    op.drop_table("clientes")
