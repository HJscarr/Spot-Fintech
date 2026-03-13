from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Account
from app.schemas import AccountCreate, AccountResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=AccountResponse)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    existing = db.query(Account).filter(Account.email == account.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    db_account = Account(
        owner_name=account.owner_name,
        email=account.email,
        balance=account.balance,
    )
    db.add(db_account)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
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
    # BUG 2: Deleting an account without checking for or cascading
    # linked transactions/portfolio items. This will cause a foreign key
    # constraint error if the account has any related records.
    db.delete(account)
    db.commit()
    return {"message": "Account deleted"}
