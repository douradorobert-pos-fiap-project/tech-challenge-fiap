import uuid

from src.application.dtos.ordem_servico_dtos import OrdemServicoResponseDTO
from src.application.ports.repositories.ordem_servico_repository_port import OrdemServicoRepositoryPort
from src.domain.exceptions.domain_exceptions import OrdemServicoNaoEncontradaError
from src.application.usecases.ordem_servico.abrir_os import AbrirOsUseCase


class DetalharOsUseCase:
    def __init__(self, repository: OrdemServicoRepositoryPort) -> None:
        self._repository = repository

    def execute(self, os_id: uuid.UUID) -> OrdemServicoResponseDTO:
        ordem = self._repository.get_by_id(os_id)
        if ordem is None:
            raise OrdemServicoNaoEncontradaError(str(os_id))
        return AbrirOsUseCase._to_response(ordem)
