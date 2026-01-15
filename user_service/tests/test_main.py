from fastapi.testclient import TestClient
from app.models import RoleEnum

def test_create_user(client: TestClient):
    response = client.post(
        "/users/",
        json={
            "email": "test@example.com", 
            "password": "password123",
            "profile": {
                "age": 25,
                "gender": "male",
                "height_cm": 180.0,
                "weight_kg": 75.0,
                "activity_level": "moderately_active",
                "goal": "maintain"
            }
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "access_token" in data
    assert "refresh_token" in data
    assert "id" in data

def test_create_existing_user(client: TestClient):
    user_data = {
        "email": "test@example.com", 
        "password": "password123",
        "profile": {
            "age": 25,
            "gender": "male",
            "height_cm": 180.0,
            "weight_kg": 75.0,
            "activity_level": "moderately_active",
            "goal": "maintain"
        }
    }
    client.post("/users/", json=user_data)
    response = client.post("/users/", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login(client: TestClient):
    # First create a user
    client.post(
        "/users/",
        json={
            "email": "login@example.com", 
            "password": "password123",
            "profile": {
                "age": 25,
                "gender": "male",
                "height_cm": 180.0,
                "weight_kg": 75.0,
                "activity_level": "moderately_active",
                "goal": "maintain"
            }
        }
    )
    
    # Test correct login
    response = client.post(
        "/login",
        json={"email": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Test incorrect password
    response = client.post(
        "/login",
        json={"email": "login@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_read_users_me(client: TestClient):
    # Create user and get token
    register_response = client.post(
        "/users/",
        json={
            "email": "me@example.com", 
            "password": "password123",
            "profile": {
                "age": 25,
                "gender": "male",
                "height_cm": 180.0,
                "weight_kg": 75.0,
                "activity_level": "moderately_active",
                "goal": "maintain"
            }
        }
    )
    token = register_response.json()["access_token"]
    
    # Test valid token
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    assert response.json()["email"] == "me@example.com"
    
    # Test invalid token
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401

def test_read_user_by_id(client: TestClient):
    register_response = client.post(
        "/users/",
        json={
            "email": "user1@example.com", 
            "password": "password123",
            "profile": {
                "age": 25,
                "gender": "male",
                "height_cm": 180.0,
                "weight_kg": 75.0,
                "activity_level": "moderately_active",
                "goal": "maintain"
            }
        }
    )
    user_id = register_response.json()["id"]
    
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "user1@example.com"
    
    response = client.get("/users/99999")
    assert response.status_code == 404