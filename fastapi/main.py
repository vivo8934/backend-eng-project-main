from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from database import get_db, Transaction
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(title="Financial Transactions API")

# Define your models and endpoints here
class TransactionSummary(BaseModel):
    total_transactions: int
    total_amount: float
    average_transaction_amount: float

@app.get("/")
async def root():
    return {"message": "Welcome to the Financial Transactions API"}

# TODO: Implement the GET /transactions/{user_id}/summary endpoint here
@app.get("/transactions/{user_id}/summary", response_model=TransactionSummary)
async def get_transaction_summary(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            func.count(Transaction.id).label("total_transactions"),
            func.sum(Transaction.amount).label("total_amount"),
            func.avg(Transaction.amount).label("average_transaction_amount")
        ).where(Transaction.user_id == user_id)
    )
    summary = result.fetchone()
    if summary is None or summary.total_transactions == 0:
        raise HTTPException(status_code=404, detail="No transactions found for this user.")
    
    return {
        "total_transactions": summary.total_transactions,
        "total_amount": summary.total_amount or 0.0,
        "average_transaction_amount": summary.average_transaction_amount or 0.0
    }