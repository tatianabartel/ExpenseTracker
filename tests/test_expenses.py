from datetime import date

from fastapi.testclient import TestClient
from app.main import app


def test_get_expenses(client: TestClient):
    response = client.get("/expenses")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_expense(client: TestClient):
    response = client.post("/expenses", json={
        "amount": 50.0,
        "category": "Food",
        "description": "Lunch",
        "date": "2023-10-01"
    })

    data = response.json()

    assert response.status_code == 200
    assert data["amount"] == 50.0
    assert data["category"] == "Food"
    assert data["description"] == "Lunch"
    assert data["date"] == "2023-10-01"


def test_create_expense_invalid_amount(client: TestClient):
    response = client.post("/expenses", json={
        "amount": -10.0,
        "category": "Food",
        "description": "Lunch",
        "date": date.today().isoformat()
    })

    assert response.status_code == 422

def test_get_nonexistent_expense(client: TestClient):
    response = client.get("/expenses/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Expense not found"}


def test_update_expense(client: TestClient):
    create_response = client.post("/expenses", json={
        "amount": 20.0,
        "category": "Transport",
        "description": "Bus fare",
        "date": date.today().isoformat()
    })

    expense_id = create_response.json()["id"]
    response = client.put(f"/expenses/{expense_id}", json={
        "amount": 25.0,
        "description": "Updated bus fare",
    })

    data = response.json()
    assert response.status_code == 200
    assert data["amount"] == 25.0
    assert data["category"] == "Transport"
    assert data["description"] == "Updated bus fare"
    assert data["date"] == date.today().isoformat()


def test_delete_expense(client: TestClient):
    create_response = client.post("/expenses", json={
        "amount": 15.0,
        "category": "Entertainment",
        "description": "Movie ticket",
        "date": date.today().isoformat()
    })

    expense_id = create_response.json()["id"]
    response = client.delete(f"/expenses/{expense_id}")

    deleted = response.json()

    assert response.status_code == 200
    assert deleted["id"] == expense_id
    assert deleted["amount"] == 15.0

    get_response = client.get(f"/expenses/{expense_id}")

    assert get_response.status_code == 404


def test_filter_by_date(client: TestClient):
    create_response1 = client.post("/expenses", json={
        "amount": 30.0,
        "category": "Groceries",
        "description": "Weekly groceries",
        "date": "2023-10-01"
    })

    create_response2 = client.post("/expenses", json={
        "amount": 40.0,
        "category": "Groceries",
        "description": "Weekly groceries",
        "date": "2023-10-05"
    })

    create_response3 = client.post("/expenses", json={
        "amount": 50.0,
        "category": "Groceries",
        "description": "Weekly groceries",
        "date": "2023-10-05"
    })

    response = client.get("/expenses?start_date=2023-10-05")
    data = response.json()

    assert response.status_code == 200
    assert all(expense["date"] >= "2023-10-05" for expense in data)



def test_summary_statistics(client: TestClient):
    client.post("/expenses", json={
        "amount": 100.0,
        "category": "Utilities",
        "description": "Electricity bill",
        "date": "2023-10-01"
    })

    client.post("/expenses", json={
        "amount": 200.0,
        "category": "Utilities",
        "description": "Water bill",
        "date": "2023-10-02"
    })

    response = client.get("/expenses/summary?start_date=2023-10-01&end_date=2023-10-02")
    data = response.json()

    assert response.status_code == 200
    assert data["total_amount"] == 300.0
    assert data["average_amount"] == 150.0
    assert data["count"] == 2


def test_filter_by_category(client: TestClient):
    client.post("/expenses", json={
        "amount": 60.0,
        "category": "Health",
        "description": "Doctor visit",
        "date": "2023-10-01"
    })

    client.post("/expenses", json={
        "amount": 80.0,
        "category": "Health",
        "description": "Medicine",
        "date": "2023-10-02"
    })

    client.post("/expenses", json={
        "amount": 50.0,
        "category": "Food",
        "description": "Dinner",
        "date": "2023-10-03"
    })

    response = client.get("/expenses?category=Health")
    data = response.json()

    assert response.status_code == 200
    assert all(expense["category"] == "Health" for expense in data)


def test_empty_database_summary(client: TestClient):
    response = client.get("/expenses/summary")
    data = response.json()

    assert response.status_code == 200
    assert data["total_amount"] == 0
    assert data["average_amount"] == 0
    assert data["count"] == 0


def test_invalid_update_expense(client: TestClient):
    create_response = client.post("/expenses", json={
        "amount": 20.0,
        "category": "Transport",
        "description": "Bus fare",
        "date": date.today().isoformat()
    })

    expense_id = create_response.json()["id"]
    response = client.put(f"/expenses/{expense_id}", json={
        "amount": -5.0,
    })

    assert response.status_code == 422


def test_update_with_null_keeps_value(client: TestClient):
    create_response = client.post("/expenses", json={
        "amount": 20.0,
        "category": "Transport",
        "description": "Bus fare",
        "date": date.today().isoformat()
    })

    expense_id = create_response.json()["id"]
    response = client.put(f"/expenses/{expense_id}", json={
        "amount": None,
        "category": None,
    })

    data = response.json()
    assert response.status_code == 200
    assert data["amount"] == 20.0
    assert data["category"] == "Transport"


def test_summary_has_no_float_rounding_error(client: TestClient):
    client.post("/expenses", json={
        "amount": 0.1,
        "category": "Food",
        "description": "Candy",
        "date": "2023-10-01"
    })

    client.post("/expenses", json={
        "amount": 0.2,
        "category": "Food",
        "description": "Gum",
        "date": "2023-10-01"
    })

    response = client.get("/expenses/summary")

    assert response.json()["total_amount"] == 0.3


def test_create_expense_too_many_decimals(client: TestClient):
    response = client.post("/expenses", json={
        "amount": 10.555,
        "category": "Food",
        "description": "Lunch",
        "date": "2023-10-01"
    })

    assert response.status_code == 422

def test_get_expenses_limit(client: TestClient):
    for i, category in enumerate(["Food", "Transport", "Other", "Helath", "Food"]):
            client.post("/expenses", json={
                "amount": i + 1,
                "category": category,
                "description": "something",
                "date": "2023-10-01"
            })
    
    response = client.get("/expenses?limit=2")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert [e["amount"] for e in data] == [1.0, 2.0]

def test_get_expenses_limit_with_offset(client: TestClient):
    for i, category in enumerate(["Food", "Transport", "Other", "Helath", "Food"]):
            client.post("/expenses", json={
                "amount": i + 1,
                "category": category,
                "description": "something",
                "date": "2023-10-01"
            })
    
    response = client.get("/expenses?limit=2&offset=2")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert [e["amount"] for e in data] == [3.0, 4.0]


def test_get_expenses_limit_greater_than_100(client: TestClient):
    response = client.get("/expenses?limit=101")

    assert response.status_code == 422