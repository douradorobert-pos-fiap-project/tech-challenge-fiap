import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from src.api.dependencies import ClienteRepoDep, CurrentUserDep
from src.application.dtos.cliente_dtos import CreateClienteDTO, UpdateClienteDTO
from src.application.usecases.cliente.crud_usecases import (
    CreateClienteUseCase,
    DeleteClienteUseCase,
    GetClienteUseCase,
    ListClientesUseCase,
    UpdateClienteUseCase,
)
from src.domain.exceptions.domain_exceptions import (
    ClienteNaoEncontradoError,
    CNPJInvalidoError,
    CPFInvalidoError,
    EmailInvalidoError,
)

router = APIRouter(prefix="/api/v1/clientes", tags=["Clientes"])


class ClienteCreateRequest(BaseModel):
    nome: str
    cpf_cnpj: str
    email: EmailStr
    telefone: str


class ClienteUpdateRequest(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    telefone: str | None = None


class ClienteResponse(BaseModel):
    id: uuid.UUID
    nome: str
    cpf_cnpj: str
    email: str
    telefone: str
    ativo: bool


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(
    req: ClienteCreateRequest,
    repo: ClienteRepoDep,
    _: CurrentUserDep,
) -> ClienteResponse:
    try:
        use_case = CreateClienteUseCase(repo)
        result = use_case.execute(
            CreateClienteDTO(
                nome=req.nome,
                cpf_cnpj=req.cpf_cnpj,
                email=req.email,
                telefone=req.telefone,
            )
        )
        return ClienteResponse(**result.__dict__)
    except (CPFInvalidoError, CNPJInvalidoError, EmailInvalidoError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[ClienteResponse])
def listar_clientes(
    repo: ClienteRepoDep,
    _: CurrentUserDep,
) -> list[ClienteResponse]:
    use_case = ListClientesUseCase(repo)
    return [ClienteResponse(**c.__dict__) for c in use_case.execute()]


@router.get("/{cliente_id}", response_model=ClienteResponse)
def obter_cliente(
    cliente_id: uuid.UUID,
    repo: ClienteRepoDep,
    _: CurrentUserDep,
) -> ClienteResponse:
    try:
        use_case = GetClienteUseCase(repo)
        result = use_case.execute(cliente_id)
        return ClienteResponse(**result.__dict__)
    except ClienteNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{cliente_id}", response_model=ClienteResponse)
def atualizar_cliente(
    cliente_id: uuid.UUID,
    req: ClienteUpdateRequest,
    repo: ClienteRepoDep,
    _: CurrentUserDep,
) -> ClienteResponse:
    try:
        use_case = UpdateClienteUseCase(repo)
        result = use_case.execute(
            cliente_id,
            UpdateClienteDTO(
                nome=req.nome,
                email=req.email,
                telefone=req.telefone,
            ),
        )
        return ClienteResponse(**result.__dict__)
    except ClienteNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except EmailInvalidoError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_cliente(
    cliente_id: uuid.UUID,
    repo: ClienteRepoDep,
    _: CurrentUserDep,
) -> None:
    try:
        use_case = DeleteClienteUseCase(repo)
        use_case.execute(cliente_id)
    except ClienteNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
