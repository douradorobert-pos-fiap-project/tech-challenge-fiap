FROM python:3.12-slim AS production

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir poetry==2.3.2 && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction

COPY src/ ./src/
COPY alembic.ini ./
COPY migrations/ ./migrations/

RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENV PYTHONPATH=/app

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
