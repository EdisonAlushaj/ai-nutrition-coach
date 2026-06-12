from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import crud, models, schemas
from .core.clients import get_user_profile
from ..database import get_db

router = APIRouter(tags=["nutrition"])


# --- Ingredient Endpoints ---

def _create_ingredient(ingredient: schemas.IngredientCreate, db: Session):
    db_ingredient = crud.get_ingredients_by_name(db, name=ingredient.name)
    if db_ingredient:
        raise HTTPException(status_code=400, detail="Ingredient with this name already exists")
    return crud.create_ingredient(db=db, ingredient=ingredient)


@router.post("/ingredients/", response_model=schemas.Ingredient)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    return _create_ingredient(ingredient, db)


@router.post("/admin/ingredients", response_model=schemas.Ingredient)
def admin_create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    return _create_ingredient(ingredient, db)


@router.get("/ingredients/", response_model=List[schemas.Ingredient])
@router.get("/ingredients", response_model=List[schemas.Ingredient])
def read_ingredients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_ingredients(db, skip=skip, limit=limit)


# --- Meal Endpoints ---

def _create_meal(meal: schemas.MealCreate, db: Session):
    return crud.create_meal(db=db, meal=meal)


@router.post("/meals/", response_model=schemas.Meal)
def create_meal(meal: schemas.MealCreate, db: Session = Depends(get_db)):
    return _create_meal(meal, db)


@router.post("/admin/meals", response_model=schemas.Meal)
def admin_create_meal(meal: schemas.MealCreate, db: Session = Depends(get_db)):
    return _create_meal(meal, db)


@router.get("/meals/", response_model=List[schemas.Meal])
@router.get("/meals", response_model=List[schemas.Meal])
def read_meals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_meals(db, skip=skip, limit=limit)


# NOTE: declared before /meals/{meal_id} so "search" is not captured as an id.
@router.get("/meals/search", response_model=List[schemas.Meal])
def search_for_meals(name: str, db: Session = Depends(get_db)):
    """Search for meals by name query."""
    meals = crud.search_meal_by_name(db, name=name)
    if not meals:
        raise HTTPException(status_code=404, detail=f"Meals not found matching '{name}'")
    return meals


@router.get("/search-food", response_model=List[schemas.Meal])
def search_food(name: str, db: Session = Depends(get_db)):
    """Gateway-facing alias of /meals/search (e.g. /search-food?name=pizza)."""
    meals = crud.search_meal_by_name(db, name=name)
    if not meals:
        raise HTTPException(status_code=404, detail=f"Meals not found matching '{name}'")
    return meals


@router.get("/meals/{meal_id}", response_model=schemas.Meal)
def read_meal(meal_id: int, db: Session = Depends(get_db)):
    """Retrieves the full details for a single meal by its ID."""
    db_meal = crud.get_meal_by_id(db, meal_id=meal_id)
    if db_meal is None:
        raise HTTPException(status_code=404, detail="Meal not found")
    return db_meal


# --- Meal Plan Endpoints ---

@router.get("/users/{user_id}/meal-plan", response_model=List[schemas.Meal])
def get_meal_plan_for_user(user_id: int, db: Session = Depends(get_db)):
    user_profile = get_user_profile(db, user_id)

    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found.")

    return crud.generate_meal_plan(db, goal=user_profile.goal)
