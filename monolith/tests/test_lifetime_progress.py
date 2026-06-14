"""Tests for lifetime progress analytics (US 2.3)."""

from datetime import date, timedelta

from app.database import SessionLocal
from app.logging_analytics import crud, models
from tests.test_smoke import PASSWORD, PROFILE

_email_counter = [700]


def _register_user(client):
    _email_counter[0] += 1
    email = f"progress{_email_counter[0]}@example.com"
    res = client.post(
        "/register",
        json={"email": email, "password": PASSWORD, "profile": PROFILE},
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def _seed_analytics(user_id: int, day: date, calories: float):
    db = SessionLocal()
    try:
        db.add(
            models.DailyAnalytics(
                user_id=user_id,
                date=day,
                total_calories=calories,
                total_protein=100,
                total_carbs=100,
                total_fat=30,
            )
        )
        db.commit()
    finally:
        db.close()


def test_lifetime_progress_empty(client):
    user_id = _register_user(client)

    res = client.get(f"/users/{user_id}/analytics/progress")
    assert res.status_code == 200
    body = res.json()
    assert body["days_tracked"] == 0
    assert body["success_rate"] == 0.0
    assert body["current_streak"] == 0


def test_lifetime_progress_success_rate(client):
    user_id = _register_user(client)
    today = date.today()

    _seed_analytics(user_id, today - timedelta(days=3), 2182)  # met at profile goal
    _seed_analytics(user_id, today - timedelta(days=2), 1500)  # under
    _seed_analytics(user_id, today - timedelta(days=1), 2200)  # met

    res = client.get(f"/users/{user_id}/analytics/progress")
    assert res.status_code == 200
    body = res.json()

    assert body["days_tracked"] == 3
    assert body["days_goal_met"] == 2
    assert body["days_under_goal"] == 1
    assert body["success_rate"] == 66.7
    assert body["tracking_since"] == (today - timedelta(days=3)).isoformat()
    assert body["daily_calorie_goal"] == 2182


def test_goal_met_streak():
    today = date.today()
    met_dates = [today - timedelta(days=2), today - timedelta(days=1), today]
    assert crud._calculate_goal_met_streak(met_dates) == 3

    broken = [today - timedelta(days=5), today - timedelta(days=1)]
    assert crud._calculate_goal_met_streak(broken) == 1
