from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from . import schemas, service

router = APIRouter(tags=["motivation"])


@router.get("/users/{user_id}/motivation/daily", response_model=schemas.MotivationQuote)
def read_daily_motivation(user_id: int, db: Session = Depends(get_db)):
    """Today's motivational quote based on the user's fitness goal (US 4.1, 4.2)."""
    from ..users import crud as users_crud

    if users_crud.get_user(db, user_id=user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return service.get_daily_quote_for_user(db, user_id)


@router.get("/users/{user_id}/motivation/random", response_model=schemas.MotivationQuote)
def read_random_motivation(
    user_id: int,
    exclude: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Fetch a new random quote for manual refresh (US 4.3)."""
    from ..users import crud as users_crud

    if users_crud.get_user(db, user_id=user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return service.get_random_quote_for_user(db, user_id, exclude=exclude)
