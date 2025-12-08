from sqlalchemy.orm import Session
from datetime import date
from . import models, schemas

def update_daily_analytics(db: Session, user_id: int, log: schemas.FoodLogCreate):
    """Finds or creates a daily analytics record for the user and updates it."""
    today = date.today()
    
    analytics = db.query(models.DailyAnalytics).filter(
        models.DailyAnalytics.user_id == user_id,
        models.DailyAnalytics.date == today
    ).first()
    
    if not analytics:
        # If no record exists for today, create a NEW one with the log's values.
        # This is the key change: we initialize the values directly.
        analytics = models.DailyAnalytics(
            user_id=user_id,
            date=today,
            total_calories=log.calories_consumed,
            total_protein=log.protein_g,
            total_carbs=log.carbs_g,
            total_fat=log.fat_g
        )
        db.add(analytics)
    else:
        # If a record already exists, just add to the totals.
        analytics.total_calories += log.calories_consumed
        analytics.total_protein += log.protein_g
        analytics.total_carbs += log.carbs_g
        analytics.total_fat += log.fat_g
    
    db.commit()

def create_food_log(db: Session, user_id: int, log: schemas.FoodLogCreate):
    db_log = models.FoodLog(
        **log.dict(),
        user_id=user_id
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    # After creating the log, update the analytics
    update_daily_analytics(db, user_id=user_id, log=log)
    
    return db_log

def get_logs_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.FoodLog).filter(models.FoodLog.user_id == user_id).offset(skip).limit(limit).all()
    
def get_analytics_for_user_date(db: Session, user_id: int, query_date: date):
    return db.query(models.DailyAnalytics).filter(
        models.DailyAnalytics.user_id == user_id,
        models.DailyAnalytics.date == query_date
    ).first()