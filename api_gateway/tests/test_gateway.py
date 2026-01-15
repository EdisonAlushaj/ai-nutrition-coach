import sys
import os
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
@patch("app.main.httpx.AsyncClient")
async def test_register_user_success(mock_client_cls):
    mock_client = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "email": "test@example.com", "is_active": True}
    mock_response.raise_for_status = MagicMock()
    
    mock_client.post.return_value = mock_response
    
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "profile": {
            "age": 25, "gender": "male", "height_cm": 180, "weight_kg": 75,
            "activity_level": "moderately_active", "goal": "maintain"
        }
    }
    
    response = client.post("/register", json=user_data)
    
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    
    mock_client.post.assert_awaited_once()
    args, kwargs = mock_client.post.call_args
    assert "user-service:8000/users/" in args[0]

@pytest.mark.asyncio
@patch("app.main.httpx.AsyncClient")
async def test_get_meals_success(mock_client_cls):
    mock_client = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"name": "Chicken Salad", "calories": 300}]
    
    mock_client.get.return_value = mock_response
    
    response = client.get("/meals")
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Chicken Salad"
    
    mock_client.get.assert_awaited_once()
    args, _ = mock_client.get.call_args
    assert "nutrition-service:8000/meals/" in args[0]

@pytest.mark.asyncio
@patch("app.main.httpx.AsyncClient")
async def test_log_food_success(mock_client_cls):
    mock_client = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 10, "food_name": "Apple"}
    
    mock_client.post.return_value = mock_response
    
    log_data = {
        "food_name": "Apple",
        "calories_consumed": 95.0,
        "protein_g": 0.5,
        "carbs_g": 25.0,
        "fat_g": 0.3
    }
    
    response = client.post("/users/1/logs", json=log_data)
    
    assert response.status_code == 200
    assert response.json()["food_name"] == "Apple"
    
    mock_client.post.assert_awaited_once()
    args, _ = mock_client.post.call_args
    assert "logging-analytics-service:8000/users/1/logs/" in args[0]

@pytest.mark.asyncio
@patch("app.main.httpx.AsyncClient")
async def test_recognize_food_success(mock_client_cls):
    mock_client = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"filename": "test.jpg", "predictions": []}
    
    mock_client.post.return_value = mock_response
    
    files = {"file": ("test.jpg", b"image_data", "image/jpeg")}
    response = client.post("/recognize-food", files=files)
    
    assert response.status_code == 200
    
    mock_client.post.assert_awaited_once()
    args, kwargs = mock_client.post.call_args
    assert "food-recognition-service:8000/predict" in args[0]
