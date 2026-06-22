import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base import Base


class OrdemServicoModel(Base):
    __tablename__ = "ordens_servico"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cliente_id: Mapped[str] = mapped_column(String(36), ForeignKey("clientes.id"), nullable=False, index=True)
    veiculo_id: Mapped[str] = mapped_column(String(36), ForeignKey("veiculos.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="RECEBIDA")
    orcamento_aprovado: Mapped[bool] = mapped_column(Boolean, default=False)
    orcamento_recusado: Mapped[bool] = mapped_column(Boolean, default=False)
    observacoes: Mapped[str] = mapped_column(String(500), default="")
    deletada: Mapped[bool] = mapped_column(Boolean, default=False)
    criada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    atualizada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    finalizada_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    entregue_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ItemServicoModel(Base):
    __tablename__ = "itens_servico"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ordem_servico_id: Mapped[str] = mapped_column(String(36), ForeignKey("ordens_servico.id"), nullable=False, index=True)
    servico_id: Mapped[str] = mapped_column(String(36), nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    preco: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)


class ItemPecaModel(Base):
    __tablename__ = "itens_peca"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ordem_servico_id: Mapped[str] = mapped_column(String(36), ForeignKey("ordens_servico.id"), nullable=False, index=True)
    peca_id: Mapped[str] = mapped_column(String(36), nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    preco_unitario: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
