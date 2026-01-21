from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from . import crud, models, schemas, security
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Logging & Analytics Service")

@app.post("/users/{user_id}/logs/", response_model=schemas.FoodLog)
def create_log_for_user(user_id: int, log: schemas.FoodLogCreate, db: Session = Depends(get_db), current_user: security.TokenPayload = Depends(security.get_current_user_from_token)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to log food for this user")

    return crud.create_food_log(db=db, user_id=user_id, log=log)

@app.get("/users/{user_id}/logs/", response_model=List[schemas.FoodLog])
def read_logs_for_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: security.TokenPayload = Depends(security.get_current_user_from_token)):
    if current_user.user_id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view logs for this user")
    
    return crud.get_logs_for_user(db=db, user_id=user_id, skip=skip, limit=limit)
    
@app.get("/users/{user_id}/analytics/{query_date}", response_model=schemas.DailyAnalytics)
def read_analytics_for_user(user_id: int, query_date: date, db: Session = Depends(get_db), current_user: security.TokenPayload = Depends(security.get_current_user_from_token)):
    if current_user.user_id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view analytics for this user") 
    
    analytics = crud.get_analytics_for_user_date(db=db, user_id=user_id, query_date=query_date)
    if analytics is None:
        return schemas.DailyAnalytics(date=query_date, total_calories=0, total_protein=0, total_carbs=0, total_fat=0)
    return analytics