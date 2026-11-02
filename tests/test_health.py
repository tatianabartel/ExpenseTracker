from sqlalchemy.exc import OperationalError

from app.database import get_db
from app.main import app


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_reports_app_env(client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "kubernetes")

    response = client.get("/health")

    assert response.json()["env"] == "kubernetes"


def test_health_defaults_to_local_env(client, monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)

    response = client.get("/health")

    assert response.json()["env"] == "local"


def test_ready_returns_ok_when_database_works(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


class BrokenSession:
    """Pretends to be a database session whose database is down."""

    def execute(self, *args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))


def test_ready_returns_503_when_database_is_down(client):
    app.dependency_overrides[get_db] = lambda: BrokenSession()

    response = client.get("/ready")

    assert response.status_code == 503