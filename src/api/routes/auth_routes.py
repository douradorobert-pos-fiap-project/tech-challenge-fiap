from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from src.api.dependencies import CurrentUserDep
from src.infrastructure.auth.jwt_handler import (
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticacao"])

ADMIN_USERNAME = "admin"
_ADMIN_PASSWORD_HASH = hash_password("secret")


def get_admin_password_hash() -> str:
    return _ADMIN_PASSWORD_HASH


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    if form_data.username != ADMIN_USERNAME or not verify_password(
        form_data.password, _ADMIN_PASSWORD_HASH
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": form_data.username, "role": "admin"})
    return TokenResponse(access_token=token)


@router.get("/me")
def me(current_user: CurrentUserDep) -> dict:
    return {"user": current_user.get("sub"), "role": current_user.get("role")}
