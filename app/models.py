from sqlalchemy import Column, Integer, String, Numeric, Date
from app.database import Base

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
