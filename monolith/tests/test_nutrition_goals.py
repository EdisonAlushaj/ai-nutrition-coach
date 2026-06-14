"""Tests for profile-based nutrition goals (US 2.4)."""

from app.users import nutrition_goals, schemas
from tests.test_smoke import PASSWORD, PROFILE

_email_counter = [600]


def _register_and_login(client):
    _email_counter[0] += 1
    email = f"goals{_email_counter[0]}@example.com"
    res = client.post(
        "/register",
        json={"email": email, "password": PASSWORD, "profile": PROFILE},
    )
    assert res.status_code == 201, res.text
    token = res.json()["access_token"]
    return res.json()["id"], token


def test_compute_nutrition_goals_from_profile():
    profile = schemas.ProfileCreate(**PROFILE)
    goals = nutrition_goals.compute_nutrition_goals(profile)

    assert goals.daily_calories == 2182
    assert goals.protein_g == 150
    assert goals.fat_g == 61
    assert goals.carbs_g == 258


def test_default_nutrition_goals_when_profile_missing():
    goals = nutrition_goals.default_nutrition_goals()
    assert goals.daily_calories == 2000
    assert goals.protein_g == 150


def test_nutrition_goals_endpoint(client):
    _, token = _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/users/me/nutrition-goals", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["daily_calories"] == 2182
    assert body["protein_g"] == 150
    assert body["fitness_goal"] == "lose_weight"


def test_nutrition_goals_by_user_id(client):
    user_id, _ = _register_and_login(client)

    res = client.get(f"/users/{user_id}/nutrition-goals")
    assert res.status_code == 200
    assert res.json()["daily_calories"] == 2182


def test_weekly_analytics_uses_profile_goal_by_default(client):
    user_id, _ = _register_and_login(client)

    res = client.get(f"/users/{user_id}/analytics/weekly")
    assert res.status_code == 200
    assert res.json()["daily_calorie_goal"] == 2182
