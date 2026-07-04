import uuid
from dataclasses import dataclass, field

from src.domain.exceptions.domain_exceptions import EstoqueInsuficienteError
from src.domain.value_objects.dinheiro import Dinheiro


@dataclass
class Peca:
    nome: str
    sku: str
    preco: Dinheiro
    quantidade_estoque: int
    estoque_minimo: int = 0
    ativo: bool = True
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome da peca e obrigatorio")
        if not self.sku or not self.sku.strip():
            raise ValueError("SKU da peca e obrigatorio")
        if self.quantidade_estoque < 0:
            raise ValueError("Quantidade em estoque nao pode ser negativa")
        if self.estoque_minimo < 0:
            raise ValueError("Estoque minimo nao pode ser negativo")

    def baixar_estoque(self, quantidade: int) -> None:
        if quantidade <= 0:
            raise ValueError("Quantidade para baixa deve ser positiva")
        if quantidade > self.quantidade_estoque:
            raise EstoqueInsuficienteError(
                self.nome, quantidade, self.quantidade_estoque
            )
        self.quantidade_estoque -= quantidade

    def repor_estoque(self, quantidade: int) -> None:
        if quantidade <= 0:
            raise ValueError("Quantidade para reposicao deve ser positiva")
        self.quantidade_estoque += quantidade

    def ajustar_estoque(self, nova_quantidade: int) -> None:
        if nova_quantidade < 0:
            raise ValueError("Quantidade ajustada nao pode ser negativa")
        self.quantidade_estoque = nova_quantidade

    @property
    def estoque_baixo(self) -> bool:
        return self.quantidade_estoque <= self.estoque_minimo

    def desativar(self) -> None:
        self.ativo = False

    def ativar(self) -> None:
        self.ativo = True

    def atualizar_dados(
        self,
        nome: str | None = None,
        preco: Dinheiro | None = None,
        estoque_minimo: int | None = None,
    ) -> None:
        if nome is not None:
            if not nome.strip():
                raise ValueError("Nome nao pode ser vazio")
            self.nome = nome
        if preco is not None:
            self.preco = preco
        if estoque_minimo is not None:
            if estoque_minimo < 0:
                raise ValueError("Estoque minimo nao pode ser negativo")
            self.estoque_minimo = estoque_minimo
