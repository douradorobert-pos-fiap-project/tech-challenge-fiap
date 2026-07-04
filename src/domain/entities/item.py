import uuid
from dataclasses import dataclass, field

from src.domain.value_objects.dinheiro import Dinheiro


@dataclass
class ItemServico:
    servico_id: uuid.UUID
    nome: str
    preco: Dinheiro
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    @property
    def subtotal(self) -> Dinheiro:
        return self.preco


@dataclass
class ItemPeca:
    peca_id: uuid.UUID
    nome: str
    preco_unitario: Dinheiro
    quantidade: int
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if self.quantidade <= 0:
            raise ValueError("Quantidade de peca deve ser positiva")

    @property
    def subtotal(self) -> Dinheiro:
        return self.preco_unitario.multiplicar(self.quantidade)
