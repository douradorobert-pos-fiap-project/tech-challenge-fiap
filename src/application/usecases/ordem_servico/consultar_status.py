import uuid

from src.application.dtos.ordem_servico_dtos import StatusOsResponseDTO
from src.application.ports.repositories.ordem_servico_repository_port import (
    OrdemServicoRepositoryPort,
)
from src.domain.exceptions.domain_exceptions import OrdemServicoNaoEncontradaError


class ConsultarStatusOsUseCase:
    def __init__(self, repository: OrdemServicoRepositoryPort) -> None:
        self._repository = repository

    def execute(self, os_id: uuid.UUID) -> StatusOsResponseDTO:
        ordem = self._repository.get_by_id(os_id)
        if ordem is None:
            raise OrdemServicoNaoEncontradaError(str(os_id))
        return StatusOsResponseDTO(id=ordem.id, status=ordem.status.name)
