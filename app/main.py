from fastapi import FastAPI

from app.database import Base, engine
from app.routes import router

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router)

@app.get("/")
async def read_root():
    return {"message": "Expense Tracker API is running!"}