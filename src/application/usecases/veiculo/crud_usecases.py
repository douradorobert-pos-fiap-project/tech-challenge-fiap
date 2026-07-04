import uuid

from src.application.dtos.veiculo_dtos import (
    CreateVeiculoDTO,
    UpdateVeiculoDTO,
    VeiculoResponseDTO,
)
from src.application.ports.repositories.cliente_repository_port import (
    ClienteRepositoryPort,
)
from src.application.ports.repositories.veiculo_repository_port import (
    VeiculoRepositoryPort,
)
from src.domain.entities.veiculo import Veiculo
from src.domain.exceptions.domain_exceptions import (
    ClienteNaoEncontradoError,
    VeiculoNaoEncontradoError,
)
from src.domain.value_objects.placa import Placa


class CreateVeiculoUseCase:
    def __init__(
        self,
        veiculo_repository: VeiculoRepositoryPort,
        cliente_repository: ClienteRepositoryPort,
    ) -> None:
        self._veiculo_repository = veiculo_repository
        self._cliente_repository = cliente_repository

    def execute(self, dto: CreateVeiculoDTO) -> VeiculoResponseDTO:
        cliente_id = uuid.UUID(dto.cliente_id)
        cliente = self._cliente_repository.get_by_id(cliente_id)
        if cliente is None:
            raise ClienteNaoEncontradoError(dto.cliente_id)

        veiculo = Veiculo(
            cliente_id=cliente_id,
            placa=Placa(dto.placa),
            marca=dto.marca,
            modelo=dto.modelo,
            ano=dto.ano,
        )
        saved = self._veiculo_repository.save(veiculo)
        return self._to_response(saved)

    @staticmethod
    def _to_response(veiculo: Veiculo) -> VeiculoResponseDTO:
        return VeiculoResponseDTO(
            id=veiculo.id,
            cliente_id=veiculo.cliente_id,
            placa=veiculo.placa.valor,
            marca=veiculo.marca,
            modelo=veiculo.modelo,
            ano=veiculo.ano,
        )


class GetVeiculoUseCase:
    def __init__(self, repository: VeiculoRepositoryPort) -> None:
        self._repository = repository

    def execute(self, veiculo_id: uuid.UUID) -> VeiculoResponseDTO:
        veiculo = self._repository.get_by_id(veiculo_id)
        if veiculo is None:
            raise VeiculoNaoEncontradoError(str(veiculo_id))
        return CreateVeiculoUseCase._to_response(veiculo)


class ListVeiculosUseCase:
    def __init__(self, repository: VeiculoRepositoryPort) -> None:
        self._repository = repository

    def execute(self) -> list[VeiculoResponseDTO]:
        veiculos = self._repository.list_all()
        return [CreateVeiculoUseCase._to_response(v) for v in veiculos]


class UpdateVeiculoUseCase:
    def __init__(self, repository: VeiculoRepositoryPort) -> None:
        self._repository = repository

    def execute(
        self, veiculo_id: uuid.UUID, dto: UpdateVeiculoDTO
    ) -> VeiculoResponseDTO:
        veiculo = self._repository.get_by_id(veiculo_id)
        if veiculo is None:
            raise VeiculoNaoEncontradoError(str(veiculo_id))
        veiculo.atualizar_dados(marca=dto.marca, modelo=dto.modelo, ano=dto.ano)
        saved = self._repository.save(veiculo)
        return CreateVeiculoUseCase._to_response(saved)


class DeleteVeiculoUseCase:
    def __init__(self, repository: VeiculoRepositoryPort) -> None:
        self._repository = repository

    def execute(self, veiculo_id: uuid.UUID) -> None:
        veiculo = self._repository.get_by_id(veiculo_id)
        if veiculo is None:
            raise VeiculoNaoEncontradoError(str(veiculo_id))
        self._repository.delete(veiculo_id)
