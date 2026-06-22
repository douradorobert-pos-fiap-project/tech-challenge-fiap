import uuid
from dataclasses import dataclass, field

from src.domain.value_objects.placa import Placa


@dataclass
class Veiculo:
    cliente_id: uuid.UUID
    placa: Placa
    marca: str
    modelo: str
    ano: int
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if not self.marca or not self.marca.strip():
            raise ValueError("Marca do veiculo e obrigatoria")
        if not self.modelo or not self.modelo.strip():
            raise ValueError("Modelo do veiculo e obrigatorio")
        if self.ano < 1900 or self.ano > 2100:
            raise ValueError("Ano do veiculo invalido")

    def atualizar_dados(
        self,
        marca: str | None = None,
        modelo: str | None = None,
        ano: int | None = None,
    ) -> None:
        if marca is not None:
            if not marca.strip():
                raise ValueError("Marca nao pode ser vazia")
            self.marca = marca
        if modelo is not None:
            if not modelo.strip():
                raise ValueError("Modelo nao pode ser vazio")
            self.modelo = modelo
        if ano is not None:
            if ano < 1900 or ano > 2100:
                raise ValueError("Ano invalido")
            self.ano = ano
