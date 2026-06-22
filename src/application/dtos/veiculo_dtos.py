import uuid
from dataclasses import dataclass


@dataclass
class CreateVeiculoDTO:
    cliente_id: str
    placa: str
    marca: str
    modelo: str
    ano: int


@dataclass
class UpdateVeiculoDTO:
    marca: str | None = None
    modelo: str | None = None
    ano: int | None = None


@dataclass
class VeiculoResponseDTO:
    id: uuid.UUID
    cliente_id: uuid.UUID
    placa: str
    marca: str
    modelo: str
    ano: int
