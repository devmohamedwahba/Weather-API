# Weather-API

## Stack

- **Framework:** FastAPI
- **Database:** Postgresql
- **Package Manager:** uv
- **Docker:** Yes
- **CI/CD:** GitHub Actions

## Getting Started

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Visit:
- **Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/api/v1/health

## Tests

```bash
uv run pytest tests/ -v
```

## Docker

```bash
docker compose up --build
```
