# Expense Tracker API

A REST API for tracking personal expenses, built with **FastAPI**, **SQLAlchemy** and **Pydantic**.
It runs on SQLite for local development and on PostgreSQL in containers, CI and Kubernetes.
The schema is managed with Alembic migrations.

## Features

- Create, read, update and delete expenses
- Filter expenses by category and date range
- Pagination: offset (`skip`/`limit`) and keyset (`after_id`), always ordered by `id`
- Summary statistics (total, count, average) for any date range, aggregated in SQL
- Input validation (positive amounts, max 2 decimal places, text length limits),
  plus a `CHECK (amount > 0)` constraint in the database
- Amounts stored as `Decimal` / `NUMERIC(10, 2)`, so there are no float rounding errors
- Liveness (`/health`) and readiness (`/ready`) endpoints for Kubernetes probes

## Tech stack

- Python 3.12
- FastAPI and Uvicorn
- SQLAlchemy 2, Alembic
- PostgreSQL 16 (psycopg 3), SQLite for local development
- Pydantic v2
- pytest
- Podman (Containerfile, compose), Kubernetes (tested on kind)
- GitHub Actions

## Getting started (local, SQLite)

```bash
git clone https://github.com/tatianabartel/ExpenseTracker
cd ExpenseTracker

python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create the schema with Alembic, then start the server:

```bash
export DATABASE_URL=sqlite:///./expenses.db    # PowerShell: $env:DATABASE_URL = "sqlite:///./expenses.db"
alembic upgrade head
uvicorn app.main:app --reload
```

The API runs at http://127.0.0.1:8000. Interactive docs are at http://127.0.0.1:8000/docs.

The app reads the database from the `DATABASE_URL` environment variable and defaults to `sqlite:///./expenses.db`.
Alembic requires `DATABASE_URL` to be set explicitly.

## Running with Podman compose (PostgreSQL)

```bash
podman compose up -d --build
podman compose exec api alembic upgrade head
```

The `api` service waits until PostgreSQL passes its `pg_isready` healthcheck.
The API is available at http://127.0.0.1:8000.

## Running on Kubernetes (kind)

The manifests in `k8s/` create a PostgreSQL Deployment with a PersistentVolumeClaim and a Secret,
a Job that runs `alembic upgrade head`, and an API Deployment with 2 replicas.

```bash
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/migrate-job.yaml
kubectl wait --for=condition=complete job/migrate --timeout=120s
kubectl apply -f k8s/api.yaml
kubectl port-forward svc/api 8000:80
```

The API image must already be loaded into the cluster as `localhost/expensetracker:dev`
(`imagePullPolicy: Never`). The Secret holds local development credentials only.

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/expenses` | List expenses. Query params: `category`, `start_date`, `end_date`, `skip` (≥ 0), `limit` (1–100, default 20), `after_id` (≥ 1, cannot be combined with `skip`) |
| `POST` | `/expenses` | Create an expense |
| `GET` | `/expenses/{id}` | Get one expense |
| `PUT` | `/expenses/{id}` | Update an expense (partial updates allowed, `null` keeps the old value) |
| `DELETE` | `/expenses/{id}` | Delete an expense |
| `GET` | `/expenses/summary` | Total, count and average, computed with `SUM`/`COUNT` in the database. Optional query params: `start_date`, `end_date` |
| `GET` | `/health` | Liveness: the process is up (does not touch the database) |
| `GET` | `/ready` | Readiness: runs `SELECT 1`, returns `503` if the database is unavailable |

### Example

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -d '{"amount": 12.50, "category": "Food", "description": "Lunch", "date": "2026-10-14"}'
```

```json
{
  "id": 1,
  "amount": 12.5,
  "category": "Food",
  "date": "2026-10-14",
  "description": "Lunch"
}
```

Keyset pagination: pass the `id` of the last item of the previous page.

```bash
curl "http://127.0.0.1:8000/expenses?limit=20&after_id=40"
```

## Database migrations

The schema is created only by Alembic (`migrations/versions/`), not by the app at startup:

1. create the `expenses` table
2. add a composite index on `(category, date)`
3. add the `CHECK (amount > 0)` constraint

```bash
alembic upgrade head      # apply all migrations
alembic downgrade -1      # undo the last one
```

## Running tests

```bash
pytest -v
```

By default the tests use an in-memory SQLite database, so your local data is never touched.
To run them against PostgreSQL, set `TEST_DATABASE_URL`.

CI (GitHub Actions) runs on every push and pull request against a PostgreSQL 16 service:
it applies the migrations, checks they are reversible (`downgrade base` + `upgrade head`), then runs pytest.

## Performance

Measured locally on PostgreSQL 16 with 1,000,000 seeded rows (`scripts/`):

- the composite index on `(category, date)` reduced a filtered query from about 70 ms to 8.7 ms
- deep pages through the API: offset pagination took about 636 ms, keyset pagination about 12 ms

## Known limitations

- No authentication
- Kubernetes credentials are a plain Secret in the repo, meant for local clusters only

## Project structure

```
ExpenseTracker/
├── app/
│   ├── main.py          # FastAPI app, includes the routers
│   ├── routes.py        # /expenses endpoints
│   ├── health.py        # /health and /ready
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas and validation
│   └── database.py      # engine, sessions, DATABASE_URL
├── migrations/          # Alembic environment and migrations
├── tests/               # pytest (expenses, pagination, health)
├── scripts/             # SQL to seed 1M rows and benchmark indexes/pagination
├── k8s/                 # Kubernetes manifests
├── .github/workflows/   # CI
├── Containerfile        # multi-stage image, non-root user
├── compose.yaml         # API + PostgreSQL
├── alembic.ini
└── requirements.txt     # pinned versions
```
