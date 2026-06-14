"""Tests for nutrition alerts (US 2.6)."""

from datetime import datetime

from app.database import SessionLocal
from app.logging_analytics import crud, models
from tests.test_smoke import PASSWORD, PROFILE

_email_counter = [500]


def _register_user(client):
    _email_counter[0] += 1
    email = f"alerts{_email_counter[0]}@example.com"
    res = client.post(
        "/register",
        json={"email": email, "password": PASSWORD, "profile": PROFILE},
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def _seed_today_analytics(user_id: int, calories: float, protein: float):
    today = datetime.now().date()
    db = SessionLocal()
    try:
        db.add(
            models.DailyAnalytics(
                user_id=user_id,
                date=today,
                total_calories=calories,
                total_protein=protein,
                total_carbs=100,
                total_fat=20,
            )
        )
        db.commit()
    finally:
        db.close()


def test_alerts_calories_over(client):
    user_id = _register_user(client)
    _seed_today_analytics(user_id, calories=2300, protein=120)

    res = client.get(f"/users/{user_id}/analytics/today/alerts")
    assert res.status_code == 200
    types = [alert["type"] for alert in res.json()["alerts"]]
    assert "calories_over" in types


def test_alerts_protein_low(client):
    user_id = _register_user(client)
    _seed_today_analytics(user_id, calories=800, protein=30)

    res = client.get(f"/users/{user_id}/analytics/today/alerts")
    assert res.status_code == 200
    types = [alert["type"] for alert in res.json()["alerts"]]
    assert "protein_low" in types


def test_alerts_clear_when_on_track(client):
    user_id = _register_user(client)
    _seed_today_analytics(user_id, calories=1950, protein=140)

    res = client.get(f"/users/{user_id}/analytics/today/alerts")
    assert res.status_code == 200
    assert res.json()["alerts"] == []


def test_get_nutrition_alerts_no_meals_logged():
    db = SessionLocal()
    try:
        noon = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
        alerts = crud.get_nutrition_alerts(db, user_id=999999, now=noon)
        assert len(alerts.alerts) == 1
        assert alerts.alerts[0].type == "no_meals_logged"
    finally:
        db.close()
