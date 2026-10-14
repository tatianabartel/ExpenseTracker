from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, PlainSerializer
from datetime import date as Date

# Decimal avoids float rounding errors; in JSON it is sent as a number, not a string
Money = Annotated[
    Decimal,
    Field(gt=0, max_digits=10, decimal_places=2),
    PlainSerializer(float, return_type=float, when_used="json"),
]


class ExpenseCreate(BaseModel):
    amount: Money
    category: str = Field(..., min_length=2, max_length=100)
    date: Date = Field(...)
    description: str = Field(..., min_length=2, max_length=200)

class ExpenseResponse(BaseModel):
    id: int
    amount: Money
    category: str
    date: Date
    description: str

    model_config = {
        "from_attributes": True}

class ExpenseUpdate(BaseModel):
    amount: Money | None = None
    category: str | None = Field(None, min_length=2, max_length=100)
    date: Date | None = Field(None)
    description: str | None = Field(None, min_length=2, max_length=200)
