import sys
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date

from app.main import app
from app.database import get_db, Base

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

TEST_USER_ID = 99

def test_daily_analytics_summation():
    """
    Tests if the daily analytics correctly sums multiple food logs for the same day.
    """
    today = date.today().isoformat()
    
    log1_data = {
        "food_name": "Test Salad",
        "calories_consumed": 350.5,
        "protein_g": 15.2,
        "carbs_g": 20.0,
        "fat_g": 25.5,
    }

    print("\n--- Posting first log ---")
    response1 = client.post(f"/users/{TEST_USER_ID}/logs/", json=log1_data)
    
    assert response1.status_code == 200, f"Failed to post first log: {response1.text}"
    print("First log posted successfully")

    print("--- Checking analytics after first log ---")
    analytics_response1 = client.get(f"/users/{TEST_USER_ID}/analytics/{today}")
    
    assert analytics_response1.status_code == 200
    analytics_data1 = analytics_response1.json()
    
    assert analytics_data1["total_calories"] == 350.5
    assert analytics_data1["total_protein"] == 15.2
    print("Analytics correct after first log.")
    
    log2_data = {
        "food_name": "Test Snack",
        "calories_consumed": 150.0,
        "protein_g": 5.0,
        "carbs_g": 30.0,
        "fat_g": 2.0
    }

    print("--- Posting second log ---")
    response2 = client.post(f"/users/{TEST_USER_ID}/logs/", json=log2_data)

    assert response2.status_code == 200, f"Failed to post second log: {response2.text}"
    print("Second log created successfully.")
    
    print("--- Checking analytics after second log ---")
    analytics_response2 = client.get(f"/users/{TEST_USER_ID}/analytics/{today}")

    assert analytics_response2.status_code == 200
    analytics_data2 = analytics_response2.json()

    assert analytics_data2["total_calories"] == 350.5 + 150.0
    assert analytics_data2["total_protein"] == 15.2 + 5.0
    print("Analytics correctly updated after second log.")
    print("--- Test Passed! ---")