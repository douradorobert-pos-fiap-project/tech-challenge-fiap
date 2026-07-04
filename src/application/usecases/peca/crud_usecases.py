import uuid

from src.application.dtos.peca_dtos import (
    AjustarEstoqueDTO,
    CreatePecaDTO,
    PecaResponseDTO,
    UpdatePecaDTO,
)
from src.application.ports.repositories.peca_repository_port import PecaRepositoryPort
from src.domain.entities.peca import Peca
from src.domain.exceptions.domain_exceptions import PecaNaoEncontradaError
from src.domain.value_objects.dinheiro import Dinheiro


class CreatePecaUseCase:
    def __init__(self, repository: PecaRepositoryPort) -> None:
        self._repository = repository

    def execute(self, dto: CreatePecaDTO) -> PecaResponseDTO:
        peca = Peca(
            nome=dto.nome,
            sku=dto.sku,
            preco=Dinheiro(dto.preco),
            quantidade_estoque=dto.quantidade_estoque,
            estoque_minimo=dto.estoque_minimo,
        )
        saved = self._repository.save(peca)
        return self._to_response(saved)

    @staticmethod
    def _to_response(peca: Peca) -> PecaResponseDTO:
        return PecaResponseDTO(
            id=peca.id,
            nome=peca.nome,
            sku=peca.sku,
            preco=float(peca.preco.valor),
            quantidade_estoque=peca.quantidade_estoque,
            estoque_minimo=peca.estoque_minimo,
            ativo=peca.ativo,
        )


class GetPecaUseCase:
    def __init__(self, repository: PecaRepositoryPort) -> None:
        self._repository = repository

    def execute(self, peca_id: uuid.UUID) -> PecaResponseDTO:
        peca = self._repository.get_by_id(peca_id)
        if peca is None:
            raise PecaNaoEncontradaError(str(peca_id))
        return CreatePecaUseCase._to_response(peca)


class ListPecasUseCase:
    def __init__(self, repository: PecaRepositoryPort) -> None:
        self._repository = repository

    def execute(self) -> list[PecaResponseDTO]:
        pecas = self._repository.list_all()
        return [CreatePecaUseCase._to_response(p) for p in pecas]


class UpdatePecaUseCase:
    def __init__(self, repository: PecaRepositoryPort) -> None:
        self._repository = repository

    def execute(self, peca_id: uuid.UUID, dto: UpdatePecaDTO) -> PecaResponseDTO:
        peca = self._repository.get_by_id(peca_id)
        if peca is None:
            raise PecaNaoEncontradaError(str(peca_id))
        preco = Dinheiro(dto.preco) if dto.preco is not None else None
        peca.atualizar_dados(
            nome=dto.nome, preco=preco, estoque_minimo=dto.estoque_minimo
        )
        saved = self._repository.save(peca)
        return CreatePecaUseCase._to_response(saved)


class AjustarEstoqueUseCase:
    def __init__(self, repository: PecaRepositoryPort) -> None:
        self._repository = repository

    def execute(self, peca_id: uuid.UUID, dto: AjustarEstoqueDTO) -> PecaResponseDTO:
        peca = self._repository.get_by_id(peca_id)
        if peca is None:
            raise PecaNaoEncontradaError(str(peca_id))
        peca.ajustar_estoque(dto.nova_quantidade)
        saved = self._repository.save(peca)
        return CreatePecaUseCase._to_response(saved)


class DeletePecaUseCase:
    def __init__(self, repository: PecaRepositoryPort) -> None:
        self._repository = repository

    def execute(self, peca_id: uuid.UUID) -> None:
        peca = self._repository.get_by_id(peca_id)
        if peca is None:
            raise PecaNaoEncontradaError(str(peca_id))
        peca.desativar()
        self._repository.save(peca)
