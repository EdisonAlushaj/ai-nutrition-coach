from pydantic import BaseModel
from typing import List, Optional
import enum

# --- Ingredient Schemas ---

class IngredientBase(BaseModel):
    name: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    id: int
    
    class Config:
        orm_mode = True

# --- Meal Schemas ---

class MealBase(BaseModel):
    name: str
    description: Optional[str] = None

class MealCreate(MealBase):
    ingredient_ids: List[int] = []

class Meal(MealBase):
    id: int
    ingredients: List[Ingredient] = []
    
    total_calories: float
    protein_g: float
    carbs_g: float
    fat_g: float

    class Config:
        orm_mode = True

# --- Food Log Schemas ---

class GoalEnum(str, enum.Enum):
    lose_weight = "lose_weight"
    maintain = "maintain"
    gain_muscle = "gain_muscle"

class UserProfile(BaseModel):
    goal: GoalEnum

    class Config:
        from_attributes = True