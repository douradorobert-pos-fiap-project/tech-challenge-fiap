import uuid
from dataclasses import dataclass


@dataclass
class CreateServicoDTO:
    nome: str
    descricao: str
    preco_base: float


@dataclass
class UpdateServicoDTO:
    nome: str | None = None
    descricao: str | None = None
    preco_base: float | None = None


@dataclass
class ServicoResponseDTO:
    id: uuid.UUID
    nome: str
    descricao: str
    preco_base: float
    ativo: bool
