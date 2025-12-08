from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class FoodLogBase(BaseModel):
    food_name: str
    calories_consumed: float
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    meal_id: Optional[int] = None

class FoodLogCreate(FoodLogBase):
    pass # The user_id will come from the URL path

class FoodLog(FoodLogBase):
    id: int
    user_id: int
    timestamp: datetime
    class Config:
        from_attributes = True

class DailyAnalytics(BaseModel):
    date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    class Config:
        from_attributes = True