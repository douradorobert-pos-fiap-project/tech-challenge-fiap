import uuid

from src.application.dtos.ordem_servico_dtos import (
    AprovarOrcamentoDTO,
    OrdemServicoResponseDTO,
)
from src.application.ports.repositories.ordem_servico_repository_port import OrdemServicoRepositoryPort
from src.domain.entities.ordem_servico import OrdemServico
from src.domain.exceptions.domain_exceptions import OrdemServicoNaoEncontradaError
from src.application.usecases.ordem_servico.abrir_os import AbrirOsUseCase


class AprovarOrcamentoUseCase:
    def __init__(self, repository: OrdemServicoRepositoryPort) -> None:
        self._repository = repository

    def execute(self, os_id: uuid.UUID, dto: AprovarOrcamentoDTO) -> OrdemServicoResponseDTO:
        ordem = self._repository.get_by_id(os_id)
        if ordem is None:
            raise OrdemServicoNaoEncontradaError(str(os_id))

        acao = dto.acao.upper()
        if acao == "APROVAR":
            ordem.aprovar_orcamento()
        elif acao == "RECUSAR":
            ordem.recusar_orcamento()
        else:
            raise ValueError(f"Acao invalida: {dto.acao}. Use APROVAR ou RECUSAR.")

        saved = self._repository.save(ordem)
        return AbrirOsUseCase._to_response(saved)
