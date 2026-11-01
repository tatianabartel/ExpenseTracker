import uuid

import pytest


def create_expenses(client, n, category):
    """Create n expenses in the given category and return their ids."""
    ids = []
    for i in range(n):
        response = client.post(
            "/expenses",
            json={
                "amount": 10 + i,
                "category": category,
                "date": "2026-11-01",
                "description": f"item {i}",
            },
        )
        assert response.status_code == 200
        ids.append(response.json()["id"])
    return ids


@pytest.fixture
def category():
    """A unique category, so each test only sees its own expenses."""
    return f"test-{uuid.uuid4().hex[:8]}"


def test_pages_do_not_overlap(client, category):
    create_expenses(client, 5, category)

    page1 = client.get("/expenses", params={"category": category, "skip": 0, "limit": 2}).json()
    page2 = client.get("/expenses", params={"category": category, "skip": 2, "limit": 2}).json()

    ids1 = [e["id"] for e in page1]
    ids2 = [e["id"] for e in page2]
    assert len(ids1) == 2
    assert len(ids2) == 2
    assert set(ids1).isdisjoint(ids2)
    assert max(ids1) < min(ids2)


def test_paging_through_everything_returns_each_item_once(client, category):
    created = create_expenses(client, 7, category)

    seen = []
    skip = 0
    while True:
        page = client.get("/expenses", params={"category": category, "skip": skip, "limit": 3}).json()
        if not page:
            break
        seen.extend(e["id"] for e in page)
        skip += 3

    assert seen == sorted(created)


def test_default_limit_is_20(client, category):
    create_expenses(client, 25, category)

    response = client.get("/expenses", params={"category": category})

    assert response.status_code == 200
    assert len(response.json()) == 20


def test_limit_100_is_allowed(client, category):
    response = client.get("/expenses", params={"category": category, "limit": 100})

    assert response.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"limit": 1000000},
        {"skip": -1},
        {"after_id": 0},
        {"after_id": -5},
    ],
)
def test_invalid_pagination_params_return_422(client, params):
    response = client.get("/expenses", params=params)

    assert response.status_code == 422


def test_after_id_pages_through_everything_once(client, category):
    created = create_expenses(client, 7, category)

    seen = []
    after_id = None
    while True:
        params = {"category": category, "limit": 3}
        if after_id is not None:
            params["after_id"] = after_id
        page = client.get("/expenses", params=params).json()
        if not page:
            break
        seen.extend(e["id"] for e in page)
        after_id = page[-1]["id"]

    assert seen == sorted(created)


def test_after_id_returns_only_newer_ids(client, category):
    created = create_expenses(client, 5, category)

    response = client.get(
        "/expenses", params={"category": category, "after_id": created[1], "limit": 10}
    )

    assert response.status_code == 200
    assert [e["id"] for e in response.json()] == created[2:]


def test_after_id_with_skip_returns_422(client, category):
    response = client.get(
        "/expenses", params={"category": category, "after_id": 1, "skip": 5}
    )

    assert response.status_code == 422
