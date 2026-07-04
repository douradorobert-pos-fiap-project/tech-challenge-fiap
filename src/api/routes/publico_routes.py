import uuid
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.api.dependencies import OsRepoDep
from src.application.usecases.ordem_servico.consultar_status import (
    ConsultarStatusOsUseCase,
)
from src.domain.exceptions.domain_exceptions import OrdemServicoNaoEncontradaError

router = APIRouter(prefix="/api/v1/public", tags=["Consulta Publica"])


class StatusOsResponse(BaseModel):
    id: uuid.UUID
    status: str


@router.get("/ordens-servico/{os_id}/status", response_model=StatusOsResponse)
def consultar_status_publico(
    os_id: uuid.UUID,
    repo: OsRepoDep,
) -> StatusOsResponse:
    try:
        use_case = ConsultarStatusOsUseCase(repo)
        result = use_case.execute(os_id)
        return StatusOsResponse(**asdict(result))
    except OrdemServicoNaoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
