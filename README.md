# ARIA Backend

Clinical decision support backend for nursing workflows. Provides patient management
and reasoning APIs over a FHIR-aligned data model.

## Tech Stack

- **Python 3.14** with strict typing
- **FastAPI** (async) for HTTP APIs and OpenAPI generation
- **SQLAlchemy 2.0** (async) with `asyncpg` driver
- **PostgreSQL 16** as the primary data store
- **Alembic** for schema migrations
- **Pydantic v2** for request/response validation and settings
- **structlog** for structured JSON logging
- **pytest** + `httpx` for async tests

## Project Layout

```
app/
├── api/v1/        # Versioned HTTP routes
├── core/          # Config, database, logging
├── models/        # SQLAlchemy ORM
├── schemas/       # Pydantic request/response models
└── services/      # Business logic
alembic/           # Database migrations
tests/             # Async test suite
```

## Quickstart

The fastest way to run the full stack:

```bash
cp .env.example .env
docker compose up --build
```

This starts PostgreSQL, applies migrations, and serves the API on
[http://localhost:8000](http://localhost:8000).

Interactive API documentation:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- OpenAPI schema: <http://localhost:8000/openapi.json>

## API Endpoints

### Patients

- `GET    /api/v1/patients`            — list patients (paginated)
- `POST   /api/v1/patients`            — create a patient
- `GET    /api/v1/patients/{id}`       — retrieve a patient

### Observations (vital signs, LOINC-coded)

- `POST   /api/v1/patients/{patient_id}/observations`         — record a vital sign
- `GET    /api/v1/patients/{patient_id}/observations`         — list a patient's observations (filters: `code`, `since`, `limit`, `offset`)
- `GET    /api/v1/patients/{patient_id}/observations/latest`  — most recent observation per code (dashboard endpoint)
- `GET    /api/v1/observations/{observation_id}`              — retrieve a single observation

## Local Development

Requirements: Python 3.14, [uv](https://docs.astral.sh/uv/) (recommended) or `pip`,
Docker for the database.

```bash
# 1. Create a virtual environment and install dependencies
uv venv
uv pip install -e ".[dev]"

# 2. Start PostgreSQL only
docker compose up -d postgres

# 3. Apply migrations
alembic upgrade head

# 4. Run the API with autoreload
uvicorn app.main:app --reload
```

## Testing

```bash
pytest
```

Tests use an in-process SQLite database via `aiosqlite`; no external services required.

## Migrations

Create a new revision after changing models:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Configuration

All runtime configuration is read from environment variables (or a `.env` file in
development). See [`.env.example`](.env.example) for the full list.

| Variable        | Purpose                                       |
|-----------------|-----------------------------------------------|
| `ENVIRONMENT`   | `development` / `staging` / `production`      |
| `DEBUG`         | Enables debug mode and verbose error output   |
| `LOG_LEVEL`     | `DEBUG` / `INFO` / `WARNING` / `ERROR`        |
| `DATABASE_URL`  | Async SQLAlchemy URL (asyncpg driver)         |
| `CORS_ORIGINS`  | Comma-separated list of allowed origins       |
