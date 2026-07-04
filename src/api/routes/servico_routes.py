import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.api.dependencies import CurrentUserDep, ServicoRepoDep
from src.application.dtos.servico_dtos import CreateServicoDTO, UpdateServicoDTO
from src.application.usecases.servico.crud_usecases import (
    CreateServicoUseCase,
    DeleteServicoUseCase,
    GetServicoUseCase,
    ListServicosUseCase,
    UpdateServicoUseCase,
)
from src.domain.exceptions.domain_exceptions import ServicoNaoEncontradoError

router = APIRouter(prefix="/api/v1/servicos", tags=["Servicos"])


class ServicoCreateRequest(BaseModel):
    nome: str
    descricao: str
    preco_base: float


class ServicoUpdateRequest(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    preco_base: float | None = None


class ServicoResponse(BaseModel):
    id: uuid.UUID
    nome: str
    descricao: str
    preco_base: float
    ativo: bool


@router.post("", response_model=ServicoResponse, status_code=status.HTTP_201_CREATED)
def criar_servico(
    req: ServicoCreateRequest,
    repo: ServicoRepoDep,
    _: CurrentUserDep,
) -> ServicoResponse:
    use_case = CreateServicoUseCase(repo)
    result = use_case.execute(
        CreateServicoDTO(
            nome=req.nome, descricao=req.descricao, preco_base=req.preco_base
        )
    )
    return ServicoResponse(**result.__dict__)


@router.get("", response_model=list[ServicoResponse])
def listar_servicos(
    repo: ServicoRepoDep,
    _: CurrentUserDep,
) -> list[ServicoResponse]:
    use_case = ListServicosUseCase(repo)
    return [ServicoResponse(**s.__dict__) for s in use_case.execute()]


@router.get("/{servico_id}", response_model=ServicoResponse)
def obter_servico(
    servico_id: uuid.UUID,
    repo: ServicoRepoDep,
    _: CurrentUserDep,
) -> ServicoResponse:
    try:
        use_case = GetServicoUseCase(repo)
        result = use_case.execute(servico_id)
        return ServicoResponse(**result.__dict__)
    except ServicoNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{servico_id}", response_model=ServicoResponse)
def atualizar_servico(
    servico_id: uuid.UUID,
    req: ServicoUpdateRequest,
    repo: ServicoRepoDep,
    _: CurrentUserDep,
) -> ServicoResponse:
    try:
        use_case = UpdateServicoUseCase(repo)
        result = use_case.execute(
            servico_id,
            UpdateServicoDTO(
                nome=req.nome,
                descricao=req.descricao,
                preco_base=req.preco_base,
            ),
        )
        return ServicoResponse(**result.__dict__)
    except ServicoNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{servico_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_servico(
    servico_id: uuid.UUID,
    repo: ServicoRepoDep,
    _: CurrentUserDep,
) -> None:
    try:
        use_case = DeleteServicoUseCase(repo)
        use_case.execute(servico_id)
    except ServicoNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
