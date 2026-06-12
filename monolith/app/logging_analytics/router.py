from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from . import crud, models, schemas
from ..database import get_db

router = APIRouter(tags=["logging-analytics"])


@router.post("/users/{user_id}/logs/", response_model=schemas.FoodLog)
@router.post("/users/{user_id}/logs", response_model=schemas.FoodLog)
def create_log_for_user(user_id: int, log: schemas.FoodLogCreate, db: Session = Depends(get_db)):
    return crud.create_food_log(db=db, user_id=user_id, log=log)


@router.get("/users/{user_id}/logs/", response_model=List[schemas.FoodLog])
@router.get("/users/{user_id}/logs", response_model=List[schemas.FoodLog])
def read_logs_for_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_logs_for_user(db=db, user_id=user_id, skip=skip, limit=limit)


# NOTE: declared before /analytics/{query_date} so "today" is not parsed as a date.
@router.get("/users/{user_id}/analytics/today", response_model=schemas.DailyAnalytics)
def read_today_analytics_for_user(user_id: int, db: Session = Depends(get_db)):
    """Convenience endpoint: nutritional summary for the current day."""
    today = date.today()
    analytics = crud.get_analytics_for_user_date(db=db, user_id=user_id, query_date=today)
    if analytics is None:
        return schemas.DailyAnalytics(date=today, total_calories=0, total_protein=0, total_carbs=0, total_fat=0)
    return analytics


@router.get("/users/{user_id}/analytics/{query_date}", response_model=schemas.DailyAnalytics)
def read_analytics_for_user(user_id: int, query_date: date, db: Session = Depends(get_db)):
    analytics = crud.get_analytics_for_user_date(db=db, user_id=user_id, query_date=query_date)
    if analytics is None:
        return schemas.DailyAnalytics(date=query_date, total_calories=0, total_protein=0, total_carbs=0, total_fat=0)
    return analytics
