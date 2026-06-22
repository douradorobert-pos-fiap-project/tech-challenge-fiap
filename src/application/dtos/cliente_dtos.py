import uuid
from dataclasses import dataclass


@dataclass
class CreateClienteDTO:
    nome: str
    cpf_cnpj: str
    email: str
    telefone: str


@dataclass
class UpdateClienteDTO:
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None


@dataclass
class ClienteResponseDTO:
    id: uuid.UUID
    nome: str
    cpf_cnpj: str
    email: str
    telefone: str
    ativo: bool
