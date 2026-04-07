# Weather API

A small HTTP API built with FastAPI that fetches current weather for a city using the [Weatherstack API](https://weatherstack.com/documentation).

## How to Use

### Setup

```bash
cp .env.example .env
# Add your Weatherstack API key to .env
uv sync
uv run uvicorn app.main:app --reload
```

### Endpoints

**GET /api/v1/current?query={city}**

Returns current weather for the given city.

```bash
curl "http://localhost:8000/api/v1/current?query=London"
```

Response:
```json
{
  "message": "Success",
  "data": {
    "request": { "type": "City", "query": "London, United Kingdom", "language": "en", "unit": "m" },
    "location": { "name": "London", "country": "United Kingdom", "region": "...", "lat": "51.517", "lon": "-0.106", "..." : "..." },
    "current": { "temperature": 15, "weather_descriptions": ["Partly cloudy"], "humidity": 72, "..." : "..." }
  }
}
```

**GET /api/v1/health** — Health check.

### Interactive Docs

Visit http://localhost:8000/docs for the Swagger UI.

### Docker

```bash
docker compose up --build
```

This starts the API on port 8000 with a Redis instance for caching.

## Tests

```bash
uv run pytest tests/ -v
```

## Assumptions & Trade-offs

- **Caching with Redis:** Weather data is cached for 1 hour (configurable via `CACHE_TTL`). Cache failures are handled gracefully — the API still works if Redis is down, it just won't cache.
- **Async HTTP client:** Uses `httpx.AsyncClient` for non-blocking HTTP calls, keeping the event loop free under concurrent load.
- **Weatherstack free tier:** The free plan only supports HTTP (not HTTPS) and a subset of fields. The schema reflects the full response structure; fields unavailable on the free tier (e.g. `astro`, `air_quality`) would need the paid plan.
- **Error mapping:** Weatherstack returns HTTP 200 even for errors (e.g. invalid key). The API detects these and raises appropriate exceptions.
- **Environment-based config:** Dev/Prod/Test configs are separated via `ENV_STATE` and env-prefixed variables.

## What I'd Improve for Production

- **Rate limiting** to protect against abuse.
- **Structured logging** with a log aggregation service instead of local file rotation.
- **API key authentication** for the weather endpoint itself.
- **More granular cache invalidation** and configurable TTL per endpoint.
- **OpenTelemetry tracing** for observability across the request lifecycle.
