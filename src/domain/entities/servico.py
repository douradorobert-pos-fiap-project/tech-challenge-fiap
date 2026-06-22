import uuid
from dataclasses import dataclass, field

from src.domain.value_objects.dinheiro import Dinheiro


@dataclass
class Servico:
    nome: str
    descricao: str
    preco_base: Dinheiro
    ativo: bool = True
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome do servico e obrigatorio")

    def desativar(self) -> None:
        self.ativo = False

    def ativar(self) -> None:
        self.ativo = True

    def atualizar_dados(
        self,
        nome: str | None = None,
        descricao: str | None = None,
        preco_base: Dinheiro | None = None,
    ) -> None:
        if nome is not None:
            if not nome.strip():
                raise ValueError("Nome nao pode ser vazio")
            self.nome = nome
        if descricao is not None:
            self.descricao = descricao
        if preco_base is not None:
            self.preco_base = preco_base
