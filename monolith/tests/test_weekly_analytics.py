"""Tests for weekly analytics summary (US 2.5)."""

from datetime import date, timedelta

from tests.test_smoke import PASSWORD, PROFILE
from app.database import SessionLocal
from app.logging_analytics import crud, models

_email_counter = [400]


def _register_user(client):
    _email_counter[0] += 1
    email = f"weekly{_email_counter[0]}@example.com"
    res = client.post(
        "/register",
        json={"email": email, "password": PASSWORD, "profile": PROFILE},
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_weekly_analytics_returns_seven_days(client):
    user_id = _register_user(client)

    res = client.get(f"/users/{user_id}/analytics/weekly")
    assert res.status_code == 200

    body = res.json()
    assert body["daily_calorie_goal"] == 2182
    assert len(body["days"]) == 7

    today = date.today()
    start = today - timedelta(days=6)
    assert body["days"][0]["date"] == start.isoformat()
    assert body["days"][-1]["date"] == today.isoformat()


def test_weekly_analytics_goal_status(client):
    user_id = _register_user(client)
    today = date.today()

    db = SessionLocal()
    try:
        db.add(
            models.DailyAnalytics(
                user_id=user_id,
                date=today - timedelta(days=2),
                total_calories=2100,
                total_protein=100,
                total_carbs=200,
                total_fat=50,
            )
        )
        db.add(
            models.DailyAnalytics(
                user_id=user_id,
                date=today - timedelta(days=1),
                total_calories=1500,
                total_protein=80,
                total_carbs=150,
                total_fat=40,
            )
        )
        db.commit()
    finally:
        db.close()

    res = client.get(f"/users/{user_id}/analytics/weekly")
    assert res.status_code == 200

    days_by_date = {day["date"]: day for day in res.json()["days"]}
    assert days_by_date[(today - timedelta(days=2)).isoformat()]["goal_status"] == "met"
    assert days_by_date[(today - timedelta(days=1)).isoformat()]["goal_status"] == "under"


def test_classify_goal_status_boundaries():
    assert crud.classify_goal_status(2000, 2000) == "met"
    assert crud.classify_goal_status(2101, 2000) == "over"
    assert crud.classify_goal_status(1899, 2000) == "under"
