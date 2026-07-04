import uuid

from src.application.dtos.cliente_dtos import (
    ClienteResponseDTO,
    CreateClienteDTO,
    UpdateClienteDTO,
)
from src.application.ports.repositories.cliente_repository_port import (
    ClienteRepositoryPort,
)
from src.domain.entities.cliente import Cliente
from src.domain.exceptions.domain_exceptions import ClienteNaoEncontradoError
from src.domain.value_objects.cpf_cnpj import CpfCnpj
from src.domain.value_objects.email import Email


class CreateClienteUseCase:
    def __init__(self, repository: ClienteRepositoryPort) -> None:
        self._repository = repository

    def execute(self, dto: CreateClienteDTO) -> ClienteResponseDTO:
        cliente = Cliente(
            nome=dto.nome,
            cpf_cnpj=CpfCnpj(dto.cpf_cnpj),
            email=Email(dto.email),
            telefone=dto.telefone,
        )
        saved = self._repository.save(cliente)
        return self._to_response(saved)

    @staticmethod
    def _to_response(cliente: Cliente) -> ClienteResponseDTO:
        return ClienteResponseDTO(
            id=cliente.id,
            nome=cliente.nome,
            cpf_cnpj=cliente.cpf_cnpj.valor,
            email=cliente.email.valor,
            telefone=cliente.telefone,
            ativo=cliente.ativo,
        )


class GetClienteUseCase:
    def __init__(self, repository: ClienteRepositoryPort) -> None:
        self._repository = repository

    def execute(self, cliente_id: uuid.UUID) -> ClienteResponseDTO:
        cliente = self._repository.get_by_id(cliente_id)
        if cliente is None:
            raise ClienteNaoEncontradoError(str(cliente_id))
        return CreateClienteUseCase._to_response(cliente)


class ListClientesUseCase:
    def __init__(self, repository: ClienteRepositoryPort) -> None:
        self._repository = repository

    def execute(self) -> list[ClienteResponseDTO]:
        clientes = self._repository.list_all()
        return [CreateClienteUseCase._to_response(c) for c in clientes]


class UpdateClienteUseCase:
    def __init__(self, repository: ClienteRepositoryPort) -> None:
        self._repository = repository

    def execute(
        self, cliente_id: uuid.UUID, dto: UpdateClienteDTO
    ) -> ClienteResponseDTO:
        cliente = self._repository.get_by_id(cliente_id)
        if cliente is None:
            raise ClienteNaoEncontradoError(str(cliente_id))
        email = Email(dto.email) if dto.email else None
        cliente.atualizar_dados(nome=dto.nome, email=email, telefone=dto.telefone)
        saved = self._repository.save(cliente)
        return CreateClienteUseCase._to_response(saved)


class DeleteClienteUseCase:
    def __init__(self, repository: ClienteRepositoryPort) -> None:
        self._repository = repository

    def execute(self, cliente_id: uuid.UUID) -> None:
        cliente = self._repository.get_by_id(cliente_id)
        if cliente is None:
            raise ClienteNaoEncontradoError(str(cliente_id))
        cliente.desativar()
        self._repository.save(cliente)
