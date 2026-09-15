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
from src.infrastructure.adapters.cpf_validator_adapter import CpfValidatorAdapter


class CreateClienteUseCase:
    def __init__(self, repository: ClienteRepositoryPort) -> None:
        self._repository = repository
        self._cpf_validator = CpfValidatorAdapter()

    def execute(self, dto: CreateClienteDTO) -> ClienteResponseDTO:
        cpf_value = CpfCnpj(dto.cpf_cnpj)

        # Validate CPF using the Lambda function (production validation)
        # In local development without Lambda ARN configured, falls back to
        # the local CpfCnpj constructor validation
        cpf_valid = self._cpf_validator.validate_cpf(cpf_value.valor)
        if not cpf_valid:
            from src.domain.exceptions.domain_exceptions import CPFInvalidoError

            raise CPFInvalidoError(cpf_value.valor)

        cliente = Cliente(
            nome=dto.nome,
            cpf_cnpj=cpf_value,
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
