import sys
import os
from unittest.mock import patch, AsyncMock

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app import schemas

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_and_read_ingredients():
    ingredient_data = {
        "name": "Chicken Breast",
        "calories_per_100g": 165.0,
        "protein_per_100g": 31.0,
        "carbs_per_100g": 0.0,
        "fat_per_100g": 3.6
    }
    response = client.post("/ingredients/", json=ingredient_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Chicken Breast"
    assert "id" in data
    ingredient_id = data["id"]

    response_get = client.get("/ingredients/")
    assert response_get.status_code == 200
    ingredients = response_get.json()
    assert len(ingredients) > 0
    assert any(i["id"] == ingredient_id for i in ingredients)

def test_create_meal():
    ing_response = client.post("/ingredients/", json={
        "name": "Rice",
        "calories_per_100g": 130.0,
        "protein_per_100g": 2.7,
        "carbs_per_100g": 28.0,
        "fat_per_100g": 0.3
    })
    assert ing_response.status_code == 200
    ing_id = ing_response.json()["id"]

    meal_data = {
        "name": "Chicken and Rice",
        "description": "Healthy lunch",
        "ingredient_ids": [ing_id] 
    }
    response = client.post("/meals/", json=meal_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Chicken and Rice"
    
    response = client.post("/meals/", json=meal_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Chicken and Rice"
    
    assert "total_calories" in data

@patch("app.main.get_user_profile", new_callable=AsyncMock)
def test_get_meal_plan(mock_get_profile):
    mock_get_profile.return_value = schemas.UserProfile(goal="maintain")
    
    user_id = 1
    response = client.get(f"/users/{user_id}/meal-plan")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)