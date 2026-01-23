from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
import enum
from typing import List

class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"

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

class ProfileBase(BaseModel):
    age: int
    gender: GenderEnum
    height_cm: float
    weight_kg: float
    activity_level: ActivityLevelEnum
    goal: GoalEnum

class ProfileCreate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    profile: ProfileCreate

class User(BaseModel):
    id: int
    email: EmailStr
    role: RoleEnum
    is_active: bool
    profile: Optional[Profile] = None
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

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

# --- Admin CMS Schemas ---

class IngredientCreate(BaseModel):
    name: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float

class Ingredient(IngredientCreate):
    id: int
    class Config:
        from_attributes = True

class MealCreate(BaseModel):
    name: str
    description: Optional[str] = None
    ingredient_ids: List[int] = []

class Meal(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    total_calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    ingredient_ids: List[int] = []
    ingredients: List[Ingredient] = []
    class Config:
        from_attributes = True