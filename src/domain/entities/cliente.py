import uuid
from dataclasses import dataclass, field

from src.domain.value_objects.cpf_cnpj import CpfCnpj
from src.domain.value_objects.email import Email


@dataclass
class Cliente:
    nome: str
    cpf_cnpj: CpfCnpj
    email: Email
    telefone: str
    ativo: bool = True
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome do cliente e obrigatorio")
        if not self.telefone or not self.telefone.strip():
            raise ValueError("Telefone do cliente e obrigatorio")

    def desativar(self) -> None:
        self.ativo = False

    def ativar(self) -> None:
        self.ativo = True

    def atualizar_dados(
        self,
        nome: str | None = None,
        email: Email | None = None,
        telefone: str | None = None,
    ) -> None:
        if nome is not None:
            if not nome.strip():
                raise ValueError("Nome do cliente nao pode ser vazio")
            self.nome = nome
        if email is not None:
            self.email = email
        if telefone is not None:
            if not telefone.strip():
                raise ValueError("Telefone nao pode ser vazio")
            self.telefone = telefone
