from sqlalchemy.orm import Session
from . import models, schemas
from .core.factory import MealPlanFactory
from typing import List

# --- Ingredient CRUD Functions ---

def get_ingredient(db: Session, ingredient_id: int):
    return db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()

def get_ingredients_by_name(db: Session, name: str):
    return db.query(models.Ingredient).filter(models.Ingredient.name == name).first()

def get_ingredients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Ingredient).offset(skip).limit(limit).all()

def create_ingredient(db: Session, ingredient: schemas.IngredientCreate):
    db_ingredient = models.Ingredient(**ingredient.dict())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

# --- Meal CRUD Functions ---

def get_meals(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Meal).offset(skip).limit(limit).all()

def create_meal(db: Session, meal: schemas.MealCreate):
    db_meal = models.Meal(name=meal.name, description=meal.description)

    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0

    for ingredient_id in meal.ingredient_ids:
        ingredient = get_ingredient(db, ingredient_id=ingredient_id)
        if ingredient:
            db_meal.ingredients.append(ingredient)
            total_calories += ingredient.calories_per_100g
            total_protein += ingredient.protein_per_100g
            total_carbs += ingredient.carbs_per_100g
            total_fat += ingredient.fat_per_100g

    db_meal.total_calories = total_calories
    db_meal.protein_g = total_protein
    db_meal.carbs_g = total_carbs
    db_meal.fat_g = total_fat

    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)

    return db_meal

# --- Meal Plan CRUD Functions ---

def generate_meal_plan(db: Session, goal: schemas.GoalEnum) -> List[models.Meal]:
    planner = MealPlanFactory.create_planner(goal)
    return planner.generate_plan(db)

def search_meal_by_name(db: Session, name: str) -> List[models.Meal]:
    """Searches for meals with names similar to the search query."""
    search_pattern = f"%{name}%"
    return db.query(models.Meal).filter(models.Meal.name.ilike(search_pattern)).limit(5).all()

def get_meal_by_id(db: Session, meal_id: int):
    """Retrieves a single meal by its unique ID."""
    return db.query(models.Meal).filter(models.Meal.id == meal_id).first()
