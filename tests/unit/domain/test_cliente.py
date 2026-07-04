import pytest

from src.domain.entities.cliente import Cliente
from src.domain.value_objects.cpf_cnpj import CpfCnpj
from src.domain.value_objects.email import Email


class TestCliente:
    def _criar_cliente_valido(self) -> Cliente:
        return Cliente(
            nome="Joao Silva",
            cpf_cnpj=CpfCnpj("52998224725"),
            email=Email("joao@example.com"),
            telefone="11999999999",
        )

    def test_criar_cliente_valido(self) -> None:
        cliente = self._criar_cliente_valido()
        assert cliente.nome == "Joao Silva"
        assert cliente.ativo is True
        assert cliente.id is not None

    def test_nome_vazio_raises_error(self) -> None:
        with pytest.raises(ValueError, match="obrigatorio"):
            Cliente(
                nome="",
                cpf_cnpj=CpfCnpj("52998224725"),
                email=Email("joao@example.com"),
                telefone="11999999999",
            )

    def test_telefone_vazio_raises_error(self) -> None:
        with pytest.raises(ValueError, match="obrigatorio"):
            Cliente(
                nome="Joao",
                cpf_cnpj=CpfCnpj("52998224725"),
                email=Email("joao@example.com"),
                telefone="",
            )

    def test_desativar_cliente(self) -> None:
        cliente = self._criar_cliente_valido()
        cliente.desativar()
        assert cliente.ativo is False

    def test_ativar_cliente(self) -> None:
        cliente = self._criar_cliente_valido()
        cliente.desativar()
        cliente.ativar()
        assert cliente.ativo is True

    def test_atualizar_nome(self) -> None:
        cliente = self._criar_cliente_valido()
        cliente.atualizar_dados(nome="Joao Santos")
        assert cliente.nome == "Joao Santos"

    def test_atualizar_email(self) -> None:
        cliente = self._criar_cliente_valido()
        novo_email = Email("novo@example.com")
        cliente.atualizar_dados(email=novo_email)
        assert cliente.email == novo_email

    def test_atualizar_nome_vazio_raises(self) -> None:
        cliente = self._criar_cliente_valido()
        with pytest.raises(ValueError, match="vazio"):
            cliente.atualizar_dados(nome="")
