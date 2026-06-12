# AI Nutrition Coach — Monolith

This folder is a **single-process (monolithic) version** of the AI Nutrition Coach
backend. It reproduces the exact public API of the microservice `api_gateway`, but
instead of forwarding every request over HTTP to separate services, all the logic
runs inside one FastAPI application and talks to a single database directly.

It exists **alongside** the original microservices — nothing in the microservice
folders was changed. You can run either architecture.

## Why it was possible to merge so cleanly

- All microservices already shared **one PostgreSQL database** → no data migration.
- The `api_gateway` was a **pure pass-through proxy** → its routing collapses into
  direct function calls.
- Model table names and class names were already unique across services → they share
  one SQLAlchemy `Base` without collisions.

The only real cross-service call (nutrition → user-service, to fetch a profile for
meal planning) was rewritten as an in-process function call in
[`app/nutrition/core/clients.py`](app/nutrition/core/clients.py).

## Structure

```
monolith/
  app/
    main.py                  # single FastAPI app: CORS, startup create_all, includes all routers
    database.py              # ONE shared engine / SessionLocal / Base / get_db
    users/                   # auth, registration, profiles  (was user_service)
    nutrition/               # meals, ingredients, meal plans (was nutrition_service)
      core/                  # planner strategy + factory + in-process user lookup
    logging_analytics/       # food logs + daily analytics    (was logging_analytics_service)
    recognition/             # ResNet50 food image prediction (was food_recognition_service)
  tests/                     # end-to-end smoke tests (SQLite)
```

Each domain keeps its own `models.py` / `schemas.py` / `crud.py` / `router.py`.
Routers expose **both** the gateway-facing paths (e.g. `/register`, `/search-food`,
`/recognize-food`, `/admin/...`) and the original service paths, so the existing
React frontend works unchanged.

## Running it

### With Docker (recommended)

From the repo root, the monolith has its own service and its **own database**
(`db-mono`), fully isolated from the microservices' data:

```bash
docker compose up --build monolith
```

- API + Swagger UI: http://localhost:8080/docs
- Monolith database (Postgres): localhost:5434  (user/password, db `mydatabase_mono`)

The microservices (port 8000) and the monolith (port 8080) can run at the same time
against separate databases.

To point the React frontend at the monolith, change `baseURL` in
`frontend/src/api/client.js` from `http://localhost:8000` to `http://localhost:8080`.

### Tests

```bash
cd monolith
pip install -r requirements.txt
pytest tests/ -q
```

Tests run against an isolated SQLite database, so they need no Postgres and no
TensorFlow.

## Notes

- **Food recognition** loads TensorFlow/ResNet50 lazily on the first `/predict`
  call. If TensorFlow is unavailable, that single router is skipped and the rest of
  the API still boots (see the guard in `app/main.py`).
- The monolith is one deployable unit: it cannot scale the recognition workload
  independently of the rest — an intentional trade-off of the monolithic design.
