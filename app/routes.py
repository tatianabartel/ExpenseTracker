from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session

from app.schemas import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.models import Expense
from app.database import get_db

router = APIRouter()


@router.post("/expenses", response_model=ExpenseResponse)
def create_expense(expense: ExpenseCreate, 
                   db: Session = Depends(get_db)):
    new_expense = Expense(
        amount=expense.amount,
        category=expense.category,
        date=expense.date,
        description=expense.description
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense


@router.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db), 
                 category: str | None = None, 
                 start_date: date | None = None, 
                 end_date: date | None = None):
    query = db.query(Expense)
    if category:
        query = query.filter(Expense.category == category)
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    expenses = query.all()
    return expenses


@router.get("/expenses/summary")
def get_expense_summary(db: Session = Depends(get_db), 
                        start_date: date | None = None, 
                        end_date: date | None = None):
    query = db.query(Expense)
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)

    expenses = query.all()
    total_amount = sum(expense.amount for expense in expenses)
    return {"total_amount": total_amount, 
            "count": len(expenses), 
            "average_amount": round(total_amount / len(expenses) if expenses else 0, 2)}


@router.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, 
                db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: int, 
                   updated_expense: ExpenseUpdate, 
                   db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    # exclude_none: an explicit null must not wipe out a required column
    update_data = updated_expense.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in update_data.items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)

    return expense


@router.delete("/expenses/{expense_id}", response_model=ExpenseResponse)
def delete_expense(expense_id: int, 
                   db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()

    return expense

