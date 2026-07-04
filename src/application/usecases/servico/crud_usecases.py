import uuid

from src.application.dtos.servico_dtos import (
    CreateServicoDTO,
    ServicoResponseDTO,
    UpdateServicoDTO,
)
from src.application.ports.repositories.servico_repository_port import (
    ServicoRepositoryPort,
)
from src.domain.entities.servico import Servico
from src.domain.exceptions.domain_exceptions import ServicoNaoEncontradoError
from src.domain.value_objects.dinheiro import Dinheiro


class CreateServicoUseCase:
    def __init__(self, repository: ServicoRepositoryPort) -> None:
        self._repository = repository

    def execute(self, dto: CreateServicoDTO) -> ServicoResponseDTO:
        servico = Servico(
            nome=dto.nome,
            descricao=dto.descricao,
            preco_base=Dinheiro(dto.preco_base),
        )
        saved = self._repository.save(servico)
        return self._to_response(saved)

    @staticmethod
    def _to_response(servico: Servico) -> ServicoResponseDTO:
        return ServicoResponseDTO(
            id=servico.id,
            nome=servico.nome,
            descricao=servico.descricao,
            preco_base=float(servico.preco_base.valor),
            ativo=servico.ativo,
        )


class GetServicoUseCase:
    def __init__(self, repository: ServicoRepositoryPort) -> None:
        self._repository = repository

    def execute(self, servico_id: uuid.UUID) -> ServicoResponseDTO:
        servico = self._repository.get_by_id(servico_id)
        if servico is None:
            raise ServicoNaoEncontradoError(str(servico_id))
        return CreateServicoUseCase._to_response(servico)


class ListServicosUseCase:
    def __init__(self, repository: ServicoRepositoryPort) -> None:
        self._repository = repository

    def execute(self) -> list[ServicoResponseDTO]:
        servicos = self._repository.list_all()
        return [CreateServicoUseCase._to_response(s) for s in servicos]


class UpdateServicoUseCase:
    def __init__(self, repository: ServicoRepositoryPort) -> None:
        self._repository = repository

    def execute(
        self, servico_id: uuid.UUID, dto: UpdateServicoDTO
    ) -> ServicoResponseDTO:
        servico = self._repository.get_by_id(servico_id)
        if servico is None:
            raise ServicoNaoEncontradoError(str(servico_id))
        preco = Dinheiro(dto.preco_base) if dto.preco_base is not None else None
        servico.atualizar_dados(
            nome=dto.nome, descricao=dto.descricao, preco_base=preco
        )
        saved = self._repository.save(servico)
        return CreateServicoUseCase._to_response(saved)


class DeleteServicoUseCase:
    def __init__(self, repository: ServicoRepositoryPort) -> None:
        self._repository = repository

    def execute(self, servico_id: uuid.UUID) -> None:
        servico = self._repository.get_by_id(servico_id)
        if servico is None:
            raise ServicoNaoEncontradoError(str(servico_id))
        servico.desativar()
        self._repository.save(servico)
