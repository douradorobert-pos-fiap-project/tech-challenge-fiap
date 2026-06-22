import uuid

from src.application.dtos.ordem_servico_dtos import OrdemServicoResponseDTO
from src.application.ports.repositories.ordem_servico_repository_port import OrdemServicoRepositoryPort
from src.application.usecases.ordem_servico.abrir_os import AbrirOsUseCase


class ListarOsUseCase:
    def __init__(self, repository: OrdemServicoRepositoryPort) -> None:
        self._repository = repository

    def execute(self) -> list[OrdemServicoResponseDTO]:
        ordens = self._repository.list_ativas()

        ordens.sort(
            key=lambda o: (
                o.status.ordem_listagem,
                o.criada_em,
            )
        )

        return [AbrirOsUseCase._to_response(o) for o in ordens]
