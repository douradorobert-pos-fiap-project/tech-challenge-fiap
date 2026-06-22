import uuid
from dataclasses import dataclass, field

from src.domain.entities.item import ItemPeca, ItemServico
from src.domain.value_objects.dinheiro import Dinheiro


@dataclass
class Orcamento:
    itens_servico: list[ItemServico] = field(default_factory=list)
    itens_peca: list[ItemPeca] = field(default_factory=list)
    aprovado: bool = False
    recusado: bool = False
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    @property
    def total_servicos(self) -> Dinheiro:
        if not self.itens_servico:
            return Dinheiro(0)
        total = self.itens_servico[0].subtotal
        for item in self.itens_servico[1:]:
            total = total.somar(item.subtotal)
        return total

    @property
    def total_pecas(self) -> Dinheiro:
        if not self.itens_peca:
            return Dinheiro(0)
        total = self.itens_peca[0].subtotal
        for item in self.itens_peca[1:]:
            total = total.somar(item.subtotal)
        return total

    @property
    def total(self) -> Dinheiro:
        return self.total_servicos.somar(self.total_pecas)

    def aprovar(self) -> None:
        if self.aprovado:
            raise ValueError("Orcamento ja foi aprovado")
        if self.recusado:
            raise ValueError("Orcamento ja foi recusado")
        self.aprovado = True

    def recusar(self) -> None:
        if self.aprovado:
            raise ValueError("Orcamento ja foi aprovado")
        if self.recusado:
            raise ValueError("Orcamento ja foi recusado")
        self.recusado = True

    @property
    def pendente(self) -> bool:
        return not self.aprovado and not self.recusado
