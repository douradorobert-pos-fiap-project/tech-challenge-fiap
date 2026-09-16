import logging
import time
import uuid
from contextlib import asynccontextmanager

import newrelic.agent
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

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
from src.infrastructure.observability.logging import (
    configure_logging,
    correlation_id_context,
    request_context,
)

configure_logging()
if settings.NEW_RELIC_LICENSE_KEY:
    newrelic.agent.initialize()
logger = logging.getLogger(__name__)


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


@app.middleware("http")
async def observability_middleware(request: Request, call_next) -> Response:
    incoming = request.headers.get("X-Correlation-ID")
    correlation_id = incoming[:128] if incoming else str(uuid.uuid4())
    correlation_token = correlation_id_context.set(correlation_id)
    request_token = request_context.set(
        {"request_method": request.method, "request_path": request.url.path}
    )
    started = time.perf_counter()
    response: Response | None = None
    try:
        response = await call_next(request)
        return response
    except Exception:
        logger.exception("Unhandled request exception")
        raise
    finally:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        if response is not None:
            response.headers["X-Correlation-ID"] = correlation_id
            request_context.set(
                {
                    "request_method": request.method,
                    "request_path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                }
            )
        logger.info("HTTP request completed")
        request_context.reset(request_token)
        correlation_id_context.reset(correlation_token)


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
