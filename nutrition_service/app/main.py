from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .core.clients import get_user_profile
from . import crud, models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Nutrition Service",
    description="Manages meals, ingredients, and nutritional data."
)

# --- Ingredient Endpoints ---

@app.post("/ingredients/", response_model=schemas.Ingredient)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    db_ingredient = crud.get_ingredients_by_name(db, name=ingredient.name)
    if db_ingredient:
        raise HTTPException(status_code=400, detail="Ingredient with this name already exists")
    return crud.create_ingredient(db=db, ingredient=ingredient)

@app.get("/ingredients/", response_model=List[schemas.Ingredient])
def read_ingredients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ingredients = crud.get_ingredients(db, skip=skip, limit=limit)
    return ingredients

# --- Meal Endpoints ---

@app.post("/meals/", response_model=schemas.Meal)
def create_meal(meal: schemas.MealCreate, db: Session = Depends(get_db)):
    return crud.create_meal(db=db, meal=meal)

@app.get("/meals/", response_model=List[schemas.Meal])
def read_meals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    meals = crud.get_meals(db, skip=skip, limit=limit)
    return meals

# --- Meal Plan Endpoints ---

@app.get("/users/{user_id}/meal-plan", response_model=List[schemas.Meal])
async def get_meal_plan_for_user(user_id: int, db: Session = Depends(get_db)):
    user_profile = await get_user_profile(user_id)
    
    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found or User Service is down.")
    
    recommended_meals = crud.generate_meal_plan(db, goal=user_profile.goal)
    
    return recommended_meals