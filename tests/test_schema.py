from datetime import date

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app.models import Expense


def test_schema_is_built_by_alembic(db):
    assert "alembic_version" in inspect(db.get_bind()).get_table_names()


def test_database_rejects_non_positive_amount(db):
    # Bypasses the API, so only the CHECK constraint from the migration can stop it
    db.add(Expense(amount=0, category="Food", description="Free lunch", date=date(2026, 11, 1)))

    with pytest.raises(IntegrityError):
        db.commit()
