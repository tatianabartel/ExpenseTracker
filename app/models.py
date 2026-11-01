from sqlalchemy import Column, Integer, String, Numeric, Date, Index, CheckConstraint
from app.database import Base

class Expense(Base):
    __tablename__ = 'expenses'
    __table_args__ = (
        Index("ix_expenses_category_date", "category", "date"),
        CheckConstraint("amount > 0", name="ck_expenses_amount_positive"),
    )

    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
