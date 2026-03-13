from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account, PortfolioItem
from app.schemas import PortfolioItemCreate, PortfolioItemResponse, PortfolioSummary

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/", response_model=PortfolioItemResponse)
def add_portfolio_item(item: PortfolioItemCreate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == item.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    db_item = PortfolioItem(
        account_id=item.account_id,
        ticker=item.ticker,
        shares=item.shares,
        purchase_price=item.purchase_price,
        current_price=item.current_price,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/summary/{account_id}", response_model=PortfolioSummary)
def get_portfolio_summary(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    items = (
        db.query(PortfolioItem)
        .filter(PortfolioItem.account_id == account_id)
        .all()
    )

    total_value = sum(item.shares * item.current_price for item in items)
    total_cost = sum(item.shares * item.purchase_price for item in items)

    gain_loss = total_value - total_cost
    gain_loss_pct = (gain_loss / total_cost * 100) if total_cost != 0 else 0.0

    return PortfolioSummary(
        account_id=account_id,
        total_value=total_value,
        total_gain_loss=gain_loss,
        gain_loss_percentage=gain_loss_pct,
        items=items,
    )
