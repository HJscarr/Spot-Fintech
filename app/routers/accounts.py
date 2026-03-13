from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Account, Transaction, PortfolioItem
from app.schemas import AccountCreate, AccountResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=AccountResponse)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    # BUG 1: No duplicate email check - allows creating multiple accounts
    # with the same email, which will crash on the DB unique constraint
    # instead of returning a friendly error.
    db_account = Account(
        owner_name=account.owner_name,
        email=account.email,
        balance=account.balance,
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.get("/", response_model=list[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).all()


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    # Check for linked transactions or portfolio items before deleting
    has_transactions = db.query(Transaction).filter(Transaction.account_id == account_id).first()
    has_portfolio = db.query(PortfolioItem).filter(PortfolioItem.account_id == account_id).first()
    if has_transactions or has_portfolio:
        raise HTTPException(
            status_code=409,
            detail="Account cannot be deleted while it has linked transactions or portfolio items.",
        )

    try:
        db.delete(account)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Account cannot be deleted while it has linked transactions or portfolio items.",
        )
    return {"message": "Account deleted"}
