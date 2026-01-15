from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from ..app.main import app
from ..app import schemas, models
from ..app.database import get_db

client = TestClient(app)

def test_registration_auto_login():
    # Mock user data
    user_data = {
        "email": "autologin@example.com",
        "password": "password123",
        "profile": {
            "age": 25,
            "gender": "male",
            "height_cm": 180,
            "weight_kg": 75,
            "activity_level": "moderately_active",
            "goal": "maintain"
        }
    }

    # Create a mock user object to return from create_user
    mock_user = models.User(
        id=1,
        email=user_data["email"],
        role=models.RoleEnum.user,
        is_active=True,
        hashed_password="hashed_secret"
    )

    # Use patch to mock crud functions
    # We need to patch where they are used in main.py, or the crud module itself
    with patch("user_service.app.crud.get_user_by_email", return_value=None) as mock_get_user, \
         patch("user_service.app.crud.create_user", return_value=mock_user) as mock_create_user:
        
        # Override get_db to avoid real DB connection if called elsewhere
        app.dependency_overrides[get_db] = lambda: MagicMock()

        response = client.post("/users/", json=user_data)
        
        # Reset overrides
        app.dependency_overrides = {}

        assert response.status_code == 200, response.text
        
        json_resp = response.json()
        
        # Verify tokens in body
        assert "access_token" in json_resp
        assert "refresh_token" in json_resp
        assert json_resp["email"] == user_data["email"]
        
        # Verify cookies
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
