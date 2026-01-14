from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
import enum

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"

class ActivityLevelEnum(str, enum.Enum):
    sedentary = "sedentary"
    lightly_active = "lightly_active"
    moderately_active = "moderately_active"
    very_active = "very_active"
    extra_active = "extra_active"

class GoalEnum(str, enum.Enum):
    lose_weight = "lose_weight"
    maintain = "maintain"
    gain_muscle = "gain_muscle"

class ProfileCreate(BaseModel):
    age: int
    gender: GenderEnum
    height_cm: float
    weight_kg: float
    activity_level: ActivityLevelEnum
    goal: GoalEnum

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    profile: ProfileCreate

class FoodLogCreate(BaseModel):
    food_name: str
    calories_consumed: float
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    meal_id: Optional[int] = None

class FoodLog(BaseModel):
    id: int
    user_id: int
    food_name: str
    calories_consumed: float
    protein_g: float
    carbs_g: float
    fat_g: float
    meal_id: Optional[int] = None
    timestamp: datetime

class DailyAnalytics(BaseModel):
    date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float