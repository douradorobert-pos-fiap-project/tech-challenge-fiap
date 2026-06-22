import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.dependencies import CurrentUserDep, PecaRepoDep
from src.application.dtos.peca_dtos import (
    AjustarEstoqueDTO,
    CreatePecaDTO,
    UpdatePecaDTO,
)
from src.application.usecases.peca.crud_usecases import (
    AjustarEstoqueUseCase,
    CreatePecaUseCase,
    DeletePecaUseCase,
    GetPecaUseCase,
    ListPecasUseCase,
    UpdatePecaUseCase,
)
from src.domain.exceptions.domain_exceptions import (
    EstoqueInsuficienteError,
    PecaNaoEncontradaError,
)

router = APIRouter(prefix="/api/v1/pecas", tags=["Pecas"])


class PecaCreateRequest(BaseModel):
    nome: str
    sku: str
    preco: float
    quantidade_estoque: int
    estoque_minimo: int = 0


class PecaUpdateRequest(BaseModel):
    nome: str | None = None
    preco: float | None = None
    estoque_minimo: int | None = None


class AjustarEstoqueRequest(BaseModel):
    nova_quantidade: int


class PecaResponse(BaseModel):
    id: uuid.UUID
    nome: str
    sku: str
    preco: float
    quantidade_estoque: int
    estoque_minimo: int
    ativo: bool


@router.post("", response_model=PecaResponse, status_code=status.HTTP_201_CREATED)
def criar_peca(
    req: PecaCreateRequest,
    repo: PecaRepoDep,
    _: CurrentUserDep,
) -> PecaResponse:
    use_case = CreatePecaUseCase(repo)
    result = use_case.execute(
        CreatePecaDTO(
            nome=req.nome,
            sku=req.sku,
            preco=req.preco,
            quantidade_estoque=req.quantidade_estoque,
            estoque_minimo=req.estoque_minimo,
        )
    )
    return PecaResponse(**result.__dict__)


@router.get("", response_model=list[PecaResponse])
def listar_pecas(
    repo: PecaRepoDep,
    _: CurrentUserDep,
) -> list[PecaResponse]:
    use_case = ListPecasUseCase(repo)
    return [PecaResponse(**p.__dict__) for p in use_case.execute()]


@router.get("/{peca_id}", response_model=PecaResponse)
def obter_peca(
    peca_id: uuid.UUID,
    repo: PecaRepoDep,
    _: CurrentUserDep,
) -> PecaResponse:
    try:
        use_case = GetPecaUseCase(repo)
        result = use_case.execute(peca_id)
        return PecaResponse(**result.__dict__)
    except PecaNaoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{peca_id}", response_model=PecaResponse)
def atualizar_peca(
    peca_id: uuid.UUID,
    req: PecaUpdateRequest,
    repo: PecaRepoDep,
    _: CurrentUserDep,
) -> PecaResponse:
    try:
        use_case = UpdatePecaUseCase(repo)
        result = use_case.execute(
            peca_id,
            UpdatePecaDTO(
                nome=req.nome,
                preco=req.preco,
                estoque_minimo=req.estoque_minimo,
            ),
        )
        return PecaResponse(**result.__dict__)
    except PecaNaoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{peca_id}/estoque", response_model=PecaResponse)
def ajustar_estoque(
    peca_id: uuid.UUID,
    req: AjustarEstoqueRequest,
    repo: PecaRepoDep,
    _: CurrentUserDep,
) -> PecaResponse:
    try:
        use_case = AjustarEstoqueUseCase(repo)
        result = use_case.execute(peca_id, AjustarEstoqueDTO(nova_quantidade=req.nova_quantidade))
        return PecaResponse(**result.__dict__)
    except PecaNaoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except EstoqueInsuficienteError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{peca_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_peca(
    peca_id: uuid.UUID,
    repo: PecaRepoDep,
    _: CurrentUserDep,
) -> None:
    try:
        use_case = DeletePecaUseCase(repo)
        use_case.execute(peca_id)
    except PecaNaoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
