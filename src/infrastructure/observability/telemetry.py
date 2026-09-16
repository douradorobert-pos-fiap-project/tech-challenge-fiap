import logging
from datetime import UTC, datetime

import newrelic.agent

from src.infrastructure.observability.logging import get_correlation_id

logger = logging.getLogger(__name__)


def record_event(event_type: str, **attributes: object) -> None:
    attributes.setdefault("timestamp", datetime.now(UTC).isoformat())
    if correlation_id := get_correlation_id():
        attributes["correlation_id"] = correlation_id
    try:
        newrelic.agent.record_custom_event(event_type, attributes)
    except Exception:
        logger.debug("Unable to record New Relic custom event", exc_info=True)


def record_integration_error(
    integration: str, operation: str, error: Exception, status_code: int | None = None
) -> None:
    attributes: dict[str, object] = {
        "integration": integration,
        "operation": operation,
        "error_type": type(error).__name__,
    }
    if status_code is not None:
        attributes["status_code"] = status_code
    record_event("IntegrationError", **attributes)
