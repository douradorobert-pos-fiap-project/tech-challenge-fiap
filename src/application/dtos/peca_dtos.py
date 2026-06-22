import uuid
from dataclasses import dataclass


@dataclass
class CreatePecaDTO:
    nome: str
    sku: str
    preco: float
    quantidade_estoque: int
    estoque_minimo: int = 0


@dataclass
class UpdatePecaDTO:
    nome: str | None = None
    preco: float | None = None
    estoque_minimo: int | None = None


@dataclass
class AjustarEstoqueDTO:
    nova_quantidade: int


@dataclass
class PecaResponseDTO:
    id: uuid.UUID
    nome: str
    sku: str
    preco: float
    quantidade_estoque: int
    estoque_minimo: int
    ativo: bool
