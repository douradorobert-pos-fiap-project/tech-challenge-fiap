FROM python:3.12-slim AS builder

ENV POETRY_VERSION=2.3.2 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY src/ ./src/

RUN poetry install --no-root

FROM python:3.12-slim AS runtime

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app/src/ ./src/

RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENV PYTHONPATH=/app \
    DATABASE_URL=sqlite:///./data/oficina.db

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
