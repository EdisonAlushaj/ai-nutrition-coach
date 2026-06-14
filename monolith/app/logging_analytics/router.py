from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from . import crud, models, schemas
from ..database import get_db
from ..users.nutrition_goals import resolve_nutrition_goals_for_user

router = APIRouter(tags=["logging-analytics"])


@router.post("/users/{user_id}/logs/", response_model=schemas.FoodLog)
@router.post("/users/{user_id}/logs", response_model=schemas.FoodLog)
def create_log_for_user(user_id: int, log: schemas.FoodLogCreate, db: Session = Depends(get_db)):
    return crud.create_food_log(db=db, user_id=user_id, log=log)


@router.get("/users/{user_id}/logs/", response_model=List[schemas.FoodLog])
@router.get("/users/{user_id}/logs", response_model=List[schemas.FoodLog])
def read_logs_for_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_logs_for_user(db=db, user_id=user_id, skip=skip, limit=limit)


# NOTE: static analytics paths must be declared before /analytics/{query_date}.
@router.get("/users/{user_id}/analytics/weekly", response_model=schemas.WeeklyAnalytics)
def read_weekly_analytics_for_user(
    user_id: int,
    daily_goal: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Nutritional summary for the last 7 days including today."""
    goals = resolve_nutrition_goals_for_user(db, user_id, daily_calories_override=daily_goal)
    return crud.get_weekly_analytics(db=db, user_id=user_id, daily_goal=goals.daily_calories)


@router.get("/users/{user_id}/analytics/progress", response_model=schemas.LifetimeProgress)
def read_lifetime_progress_for_user(
    user_id: int,
    daily_goal: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Goal adherence since the user first started logging food (US 2.3)."""
    goals = resolve_nutrition_goals_for_user(db, user_id, daily_calories_override=daily_goal)
    return crud.get_lifetime_progress(db=db, user_id=user_id, daily_goal=goals.daily_calories)


@router.get("/users/{user_id}/analytics/today/alerts", response_model=schemas.NutritionAlertsResponse)
def read_today_nutrition_alerts(
    user_id: int,
    daily_goal: Optional[float] = None,
    protein_goal: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Nutrition warnings for today based on current intake vs goals (US 2.6)."""
    goals = resolve_nutrition_goals_for_user(
        db,
        user_id,
        daily_calories_override=daily_goal,
        protein_g_override=protein_goal,
    )
    return crud.get_nutrition_alerts(
        db=db,
        user_id=user_id,
        daily_goal=goals.daily_calories,
        protein_goal=goals.protein_g,
    )


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
