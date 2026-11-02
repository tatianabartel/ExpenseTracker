from pathlib import Path

from app.database import get_db
from app.main import app
from app.models import Expense

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import pytest, os

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
ALEMBIC_INI = Path(__file__).resolve().parent.parent / "alembic.ini"

if TEST_DATABASE_URL.startswith("sqlite"):
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
else:
    test_engine = create_engine(TEST_DATABASE_URL)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture(scope="session")
def migrated_database():
    # Build the schema with the same Alembic migrations as production, not create_all
    config = Config(str(ALEMBIC_INI))
    with test_engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")


@pytest.fixture
def client(db):
    def override_get_db():
        return db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def db(migrated_database):
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        # Empty the table so the next test starts clean, but keep the migrated schema
        db.rollback()
        db.execute(delete(Expense))
        db.commit()
        db.close()
