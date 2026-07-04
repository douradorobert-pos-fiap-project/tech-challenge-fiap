import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.api.dependencies import ClienteRepoDep, CurrentUserDep, VeiculoRepoDep
from src.application.dtos.veiculo_dtos import CreateVeiculoDTO, UpdateVeiculoDTO
from src.application.usecases.veiculo.crud_usecases import (
    CreateVeiculoUseCase,
    DeleteVeiculoUseCase,
    GetVeiculoUseCase,
    ListVeiculosUseCase,
    UpdateVeiculoUseCase,
)
from src.domain.exceptions.domain_exceptions import (
    ClienteNaoEncontradoError,
    PlacaInvalidaError,
    VeiculoNaoEncontradoError,
)

router = APIRouter(prefix="/api/v1/veiculos", tags=["Veiculos"])


class VeiculoCreateRequest(BaseModel):
    cliente_id: str
    placa: str
    marca: str
    modelo: str
    ano: int


class VeiculoUpdateRequest(BaseModel):
    marca: str | None = None
    modelo: str | None = None
    ano: int | None = None


class VeiculoResponse(BaseModel):
    id: uuid.UUID
    cliente_id: uuid.UUID
    placa: str
    marca: str
    modelo: str
    ano: int


@router.post("", response_model=VeiculoResponse, status_code=status.HTTP_201_CREATED)
def criar_veiculo(
    req: VeiculoCreateRequest,
    veiculo_repo: VeiculoRepoDep,
    cliente_repo: ClienteRepoDep,
    _: CurrentUserDep,
) -> VeiculoResponse:
    try:
        use_case = CreateVeiculoUseCase(veiculo_repo, cliente_repo)
        result = use_case.execute(
            CreateVeiculoDTO(
                cliente_id=req.cliente_id,
                placa=req.placa,
                marca=req.marca,
                modelo=req.modelo,
                ano=req.ano,
            )
        )
        return VeiculoResponse(**result.__dict__)
    except ClienteNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PlacaInvalidaError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[VeiculoResponse])
def listar_veiculos(
    repo: VeiculoRepoDep,
    _: CurrentUserDep,
) -> list[VeiculoResponse]:
    use_case = ListVeiculosUseCase(repo)
    return [VeiculoResponse(**v.__dict__) for v in use_case.execute()]


@router.get("/{veiculo_id}", response_model=VeiculoResponse)
def obter_veiculo(
    veiculo_id: uuid.UUID,
    repo: VeiculoRepoDep,
    _: CurrentUserDep,
) -> VeiculoResponse:
    try:
        use_case = GetVeiculoUseCase(repo)
        result = use_case.execute(veiculo_id)
        return VeiculoResponse(**result.__dict__)
    except VeiculoNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{veiculo_id}", response_model=VeiculoResponse)
def atualizar_veiculo(
    veiculo_id: uuid.UUID,
    req: VeiculoUpdateRequest,
    repo: VeiculoRepoDep,
    _: CurrentUserDep,
) -> VeiculoResponse:
    try:
        use_case = UpdateVeiculoUseCase(repo)
        result = use_case.execute(
            veiculo_id,
            UpdateVeiculoDTO(marca=req.marca, modelo=req.modelo, ano=req.ano),
        )
        return VeiculoResponse(**result.__dict__)
    except VeiculoNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{veiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_veiculo(
    veiculo_id: uuid.UUID,
    repo: VeiculoRepoDep,
    _: CurrentUserDep,
) -> None:
    try:
        use_case = DeleteVeiculoUseCase(repo)
        use_case.execute(veiculo_id)
    except VeiculoNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
