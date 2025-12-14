from fastapi.testclient import TestClient
from ..app.main import app

client = TestClient(app)

def test_create_user_fails_if_email_exists():
    user_data = {
      "email": "test@example.com",
      "password": "a_strong_password",
      "profile": {
        "age": 30, "gender": "male", "height_cm": 180,
        "weight_kg": 75, "activity_level": "moderately_active", "goal": "maintain"
      }
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200

    response_fail = client.post("/users/", json=user_data)
    assert response_fail.status_code == 400
    assert response_fail.json() == {"detail": "Email already registered"}