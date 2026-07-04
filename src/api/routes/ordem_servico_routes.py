import uuid
from dataclasses import asdict
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.api.dependencies import (
    ClienteRepoDep,
    CurrentUserDep,
    OsRepoDep,
    PecaRepoDep,
    ServicoRepoDep,
    VeiculoRepoDep,
)
from src.application.dtos.ordem_servico_dtos import (
    AbrirOsDTO,
    AprovarOrcamentoDTO,
    AtualizarStatusDTO,
    ItemPecaInputDTO,
    ItemServicoInputDTO,
)
from src.application.usecases.ordem_servico.abrir_os import AbrirOsUseCase
from src.application.usecases.ordem_servico.aprovar_orcamento import (
    AprovarOrcamentoUseCase,
)
from src.application.usecases.ordem_servico.atualizar_status import (
    AtualizarStatusOsUseCase,
)
from src.application.usecases.ordem_servico.detalhar_os import DetalharOsUseCase
from src.application.usecases.ordem_servico.listar_os import ListarOsUseCase
from src.domain.exceptions.domain_exceptions import (
    OrcamentoJaAprovadoError,
    OrcamentoJaRecusadoError,
    OrdemServicoNaoEncontradaError,
    TransicaoStatusInvalidaError,
)

router = APIRouter(prefix="/api/v1/ordens-servico", tags=["Ordens de Servico"])


class ItemServicoRequest(BaseModel):
    servico_id: str


class ItemPecaRequest(BaseModel):
    peca_id: str
    quantidade: int


class AbrirOsRequest(BaseModel):
    cliente_id: str
    veiculo_id: str
    servicos: list[ItemServicoRequest]
    pecas: list[ItemPecaRequest]


class AprovarOrcamentoRequest(BaseModel):
    acao: str  # "APROVAR" | "RECUSAR"


class AtualizarStatusRequest(BaseModel):
    novo_status: str


class ItemServicoResponse(BaseModel):
    servico_id: uuid.UUID
    nome: str
    preco: float


class ItemPecaResponse(BaseModel):
    peca_id: uuid.UUID
    nome: str
    preco_unitario: float
    quantidade: int
    subtotal: float


class OrcamentoResponse(BaseModel):
    total_servicos: float
    total_pecas: float
    total: float
    aprovado: bool
    recusado: bool
    itens_servico: list[ItemServicoResponse]
    itens_peca: list[ItemPecaResponse]


class OrdemServicoResponse(BaseModel):
    id: uuid.UUID
    cliente_id: uuid.UUID
    veiculo_id: uuid.UUID
    status: str
    orcamento: OrcamentoResponse
    criada_em: datetime
    atualizada_em: datetime


class StatusOsResponse(BaseModel):
    id: uuid.UUID
    status: str


@router.post(
    "", response_model=OrdemServicoResponse, status_code=status.HTTP_201_CREATED
)
def abrir_os(
    req: AbrirOsRequest,
    os_repo: OsRepoDep,
    cliente_repo: ClienteRepoDep,
    veiculo_repo: VeiculoRepoDep,
    servico_repo: ServicoRepoDep,
    peca_repo: PecaRepoDep,
    _: CurrentUserDep,
) -> OrdemServicoResponse:
    try:
        use_case = AbrirOsUseCase(
            os_repo, cliente_repo, veiculo_repo, servico_repo, peca_repo
        )
        result = use_case.execute(
            AbrirOsDTO(
                cliente_id=req.cliente_id,
                veiculo_id=req.veiculo_id,
                servicos=[
                    ItemServicoInputDTO(servico_id=s.servico_id) for s in req.servicos
                ],
                pecas=[
                    ItemPecaInputDTO(peca_id=p.peca_id, quantidade=p.quantidade)
                    for p in req.pecas
                ],
            )
        )
        return OrdemServicoResponse(**asdict(result))
    except Exception as e:
        if "NaoEncontrado" in type(e).__name__:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[OrdemServicoResponse])
def listar_os(
    repo: OsRepoDep,
    _: CurrentUserDep,
) -> list[OrdemServicoResponse]:
    use_case = ListarOsUseCase(repo)
    return [OrdemServicoResponse(**asdict(o)) for o in use_case.execute()]


@router.get("/{os_id}", response_model=OrdemServicoResponse)
def detalhar_os(
    os_id: uuid.UUID,
    repo: OsRepoDep,
    _: CurrentUserDep,
) -> OrdemServicoResponse:
    try:
        use_case = DetalharOsUseCase(repo)
        result = use_case.execute(os_id)
        return OrdemServicoResponse(**asdict(result))
    except OrdemServicoNaoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{os_id}/status", response_model=OrdemServicoResponse)
def atualizar_status(
    os_id: uuid.UUID,
    req: AtualizarStatusRequest,
    repo: OsRepoDep,
    _: CurrentUserDep,
) -> OrdemServicoResponse:
    try:
        use_case = AtualizarStatusOsUseCase(repo)
        result = use_case.execute(
            os_id, AtualizarStatusDTO(novo_status=req.novo_status)
        )
        return OrdemServicoResponse(**asdict(result))
    except OrdemServicoNaoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TransicaoStatusInvalidaError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{os_id}/orcamento/aprovar", response_model=OrdemServicoResponse)
def aprovar_orcamento(
    os_id: uuid.UUID,
    req: AprovarOrcamentoRequest,
    repo: OsRepoDep,
) -> OrdemServicoResponse:
    try:
        use_case = AprovarOrcamentoUseCase(repo)
        result = use_case.execute(os_id, AprovarOrcamentoDTO(acao=req.acao))
        return OrdemServicoResponse(**asdict(result))
    except OrdemServicoNaoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (OrcamentoJaAprovadoError, OrcamentoJaRecusadoError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
