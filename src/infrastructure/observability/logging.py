import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime

from src.infrastructure.config.settings import settings

correlation_id_context: ContextVar[str | None] = ContextVar(
    "correlation_id", default=None
)
request_context: ContextVar[dict[str, object]] = ContextVar(
    "request_context", default={}
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": settings.NEW_RELIC_APP_NAME or settings.APP_NAME,
            "environment": settings.NEW_RELIC_ENVIRONMENT or settings.APP_ENV,
        }
        if correlation_id := correlation_id_context.get():
            payload["correlation_id"] = correlation_id
        payload.update(request_context.get())
        if record.exc_info:
            payload["exception_type"] = record.exc_info[0].__name__
            payload["exception_message"] = str(record.exc_info[1])
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


def get_correlation_id() -> str | None:
    return correlation_id_context.get()
