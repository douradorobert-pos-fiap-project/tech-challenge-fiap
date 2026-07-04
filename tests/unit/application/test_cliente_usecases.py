import uuid

import pytest

from src.application.dtos.cliente_dtos import CreateClienteDTO, UpdateClienteDTO
from src.application.ports.repositories.cliente_repository_port import (
    ClienteRepositoryPort,
)
from src.application.usecases.cliente.crud_usecases import (
    CreateClienteUseCase,
    DeleteClienteUseCase,
    GetClienteUseCase,
    ListClientesUseCase,
    UpdateClienteUseCase,
)
from src.domain.entities.cliente import Cliente
from src.domain.exceptions.domain_exceptions import ClienteNaoEncontradoError


class FakeClienteRepository(ClienteRepositoryPort):
    def __init__(self) -> None:
        self._clientes: dict[uuid.UUID, Cliente] = {}

    def save(self, cliente: Cliente) -> Cliente:
        self._clientes[cliente.id] = cliente
        return cliente

    def get_by_id(self, cliente_id: uuid.UUID) -> Cliente | None:
        return self._clientes.get(cliente_id)

    def get_by_cpf_cnpj(self, cpf_cnpj: str) -> Cliente | None:
        for cliente in self._clientes.values():
            if cliente.cpf_cnpj.valor == cpf_cnpj:
                return cliente
        return None

    def list_all(self) -> list[Cliente]:
        return list(self._clientes.values())

    def delete(self, cliente_id: uuid.UUID) -> None:
        self._clientes.pop(cliente_id, None)


class TestCreateClienteUseCase:
    def test_criar_cliente_com_sucesso(self) -> None:
        repo = FakeClienteRepository()
        use_case = CreateClienteUseCase(repo)

        result = use_case.execute(
            CreateClienteDTO(
                nome="Joao Silva",
                cpf_cnpj="52998224725",
                email="joao@example.com",
                telefone="11999999999",
            )
        )

        assert result.id is not None
        assert result.nome == "Joao Silva"
        assert result.cpf_cnpj == "52998224725"
        assert result.email == "joao@example.com"
        assert result.ativo is True

    def test_criar_cliente_cnpj(self) -> None:
        repo = FakeClienteRepository()
        use_case = CreateClienteUseCase(repo)

        result = use_case.execute(
            CreateClienteDTO(
                nome="Empresa XYZ",
                cpf_cnpj="11444777000161",
                email="contato@xyz.com",
                telefone="1133333333",
            )
        )

        assert result.nome == "Empresa XYZ"
        assert result.cpf_cnpj == "11444777000161"


class TestGetClienteUseCase:
    def test_obter_cliente_existente(self) -> None:
        repo = FakeClienteRepository()
        create_uc = CreateClienteUseCase(repo)
        created = create_uc.execute(
            CreateClienteDTO(
                nome="Joao",
                cpf_cnpj="52998224725",
                email="joao@example.com",
                telefone="11999999999",
            )
        )

        get_uc = GetClienteUseCase(repo)
        result = get_uc.execute(created.id)

        assert result.id == created.id
        assert result.nome == "Joao"

    def test_obter_cliente_inexistente_raises(self) -> None:
        repo = FakeClienteRepository()
        get_uc = GetClienteUseCase(repo)

        with pytest.raises(ClienteNaoEncontradoError):
            get_uc.execute(uuid.uuid4())


class TestListClientesUseCase:
    def test_listar_multiplos_clientes(self) -> None:
        repo = FakeClienteRepository()
        create_uc = CreateClienteUseCase(repo)
        create_uc.execute(
            CreateClienteDTO(
                nome="Joao", cpf_cnpj="52998224725", email="joao@ex.com", telefone="111"
            )
        )
        create_uc.execute(
            CreateClienteDTO(
                nome="Maria",
                cpf_cnpj="11144477735",
                email="maria@ex.com",
                telefone="222",
            )
        )

        list_uc = ListClientesUseCase(repo)
        result = list_uc.execute()

        assert len(result) == 2

    def test_listar_vazio(self) -> None:
        repo = FakeClienteRepository()
        list_uc = ListClientesUseCase(repo)
        assert list_uc.execute() == []


class TestUpdateClienteUseCase:
    def test_atualizar_nome(self) -> None:
        repo = FakeClienteRepository()
        create_uc = CreateClienteUseCase(repo)
        created = create_uc.execute(
            CreateClienteDTO(
                nome="Joao", cpf_cnpj="52998224725", email="joao@ex.com", telefone="111"
            )
        )

        update_uc = UpdateClienteUseCase(repo)
        result = update_uc.execute(created.id, UpdateClienteDTO(nome="Joao Santos"))

        assert result.nome == "Joao Santos"

    def test_atualizar_inexistente_raises(self) -> None:
        repo = FakeClienteRepository()
        update_uc = UpdateClienteUseCase(repo)

        with pytest.raises(ClienteNaoEncontradoError):
            update_uc.execute(uuid.uuid4(), UpdateClienteDTO(nome="X"))


class TestDeleteClienteUseCase:
    def test_desativar_cliente(self) -> None:
        repo = FakeClienteRepository()
        create_uc = CreateClienteUseCase(repo)
        created = create_uc.execute(
            CreateClienteDTO(
                nome="Joao", cpf_cnpj="52998224725", email="joao@ex.com", telefone="111"
            )
        )

        delete_uc = DeleteClienteUseCase(repo)
        delete_uc.execute(created.id)

        cliente = repo.get_by_id(created.id)
        assert cliente is not None
        assert cliente.ativo is False

    def test_deletar_inexistente_raises(self) -> None:
        repo = FakeClienteRepository()
        delete_uc = DeleteClienteUseCase(repo)

        with pytest.raises(ClienteNaoEncontradoError):
            delete_uc.execute(uuid.uuid4())
