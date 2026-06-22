import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.infrastructure.auth.jwt_handler import decode_access_token
from src.infrastructure.database.repositories.cliente_repository import SqlAlchemyClienteRepository
from src.infrastructure.database.repositories.ordem_servico_repository import (
    SqlAlchemyOrdemServicoRepository,
)
from src.infrastructure.database.repositories.peca_repository import SqlAlchemyPecaRepository
from src.infrastructure.database.repositories.servico_repository import SqlAlchemyServicoRepository
from src.infrastructure.database.repositories.veiculo_repository import SqlAlchemyVeiculoRepository
from src.infrastructure.database.session import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

SessionDep = Annotated[Session, Depends(get_session)]


def get_cliente_repository(session: SessionDep) -> SqlAlchemyClienteRepository:
    return SqlAlchemyClienteRepository(session)


def get_veiculo_repository(session: SessionDep) -> SqlAlchemyVeiculoRepository:
    return SqlAlchemyVeiculoRepository(session)


def get_servico_repository(session: SessionDep) -> SqlAlchemyServicoRepository:
    return SqlAlchemyServicoRepository(session)


def get_peca_repository(session: SessionDep) -> SqlAlchemyPecaRepository:
    return SqlAlchemyPecaRepository(session)


def get_os_repository(session: SessionDep) -> SqlAlchemyOrdemServicoRepository:
    return SqlAlchemyOrdemServicoRepository(session)


ClienteRepoDep = Annotated[SqlAlchemyClienteRepository, Depends(get_cliente_repository)]
VeiculoRepoDep = Annotated[SqlAlchemyVeiculoRepository, Depends(get_veiculo_repository)]
ServicoRepoDep = Annotated[SqlAlchemyServicoRepository, Depends(get_servico_repository)]
PecaRepoDep = Annotated[SqlAlchemyPecaRepository, Depends(get_peca_repository)]
OsRepoDep = Annotated[SqlAlchemyOrdemServicoRepository, Depends(get_os_repository)]


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


CurrentUserDep = Annotated[dict, Depends(get_current_user)]
