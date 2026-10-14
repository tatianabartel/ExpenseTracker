# Expense Tracker API

A REST API for tracking personal expenses, built with **FastAPI**, **SQLAlchemy** and **Pydantic**.

## Features

- Create, read, update and delete expenses
- Filter expenses by category and date range
- Summary statistics (total, count, average) for any date range
- Input validation (positive amounts, max 2 decimal places, text length limits)
- Amounts stored as `Decimal`, so there are no float rounding errors
- Test suite with pytest and an in-memory SQLite database

## Tech stack

- Python 3.11
- FastAPI and Uvicorn
- SQLAlchemy 2 with SQLite
- Pydantic v2
- pytest

## Getting started

```bash
git clone https://github.com/tatianabartel/ExpenseTracker
cd ExpenseTracker

python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install dependencies and run the server:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at http://127.0.0.1:8000. Interactive docs are at http://127.0.0.1:8000/docs.

By default the data is stored in `expenses.db` (SQLite). To use a different database, set the `DATABASE_URL` environment variable.

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/expenses` | List expenses. Optional query params: `category`, `start_date`, `end_date` |
| `POST` | `/expenses` | Create an expense |
| `GET` | `/expenses/{id}` | Get one expense |
| `PUT` | `/expenses/{id}` | Update an expense (partial updates allowed) |
| `DELETE` | `/expenses/{id}` | Delete an expense |
| `GET` | `/expenses/summary` | Total, count and average. Optional query params: `start_date`, `end_date` |

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

## Running tests

```bash
pytest -v
```

The tests use an in-memory SQLite database, so your local data is never touched.

## Project structure

```
ExpenseTracker/
├── app/
│   ├── main.py        # FastAPI app and startup
│   ├── routes.py      # API endpoints
│   ├── models.py      # SQLAlchemy models
│   ├── schemas.py     # Pydantic schemas and validation
│   └── database.py    # Database connection and session
├── tests/
│   ├── conftest.py    # Test fixtures (in-memory DB)
│   └── test_expenses.py
└── requirements.txt
```
