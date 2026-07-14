from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import (
    auth_routes,
    cliente_routes,
    ordem_servico_routes,
    peca_routes,
    publico_routes,
    servico_routes,
    veiculo_routes,
)
from src.infrastructure.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema Integrado de Atendimento e Execucao de Servicos para Oficina Mecanica",
    lifespan=lifespan,
    swagger_ui_parameters={"docExpansion": "none"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(cliente_routes.router)
app.include_router(veiculo_routes.router)
app.include_router(servico_routes.router)
app.include_router(peca_routes.router)
app.include_router(ordem_servico_routes.router)
app.include_router(publico_routes.router)


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
