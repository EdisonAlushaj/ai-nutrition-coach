"""Tests for manual food entry (US 3.4)."""

from tests.test_smoke import PASSWORD, PROFILE

_email_counter = [300]


def _register_user(client):
    _email_counter[0] += 1
    email = f"manual{_email_counter[0]}@example.com"
    res = client.post(
        "/register",
        json={"email": email, "password": PASSWORD, "profile": PROFILE},
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_manual_food_log_success(client):
    user_id = _register_user(client)

    res = client.post(
        f"/users/{user_id}/logs",
        json={
            "food_name": "Homemade Protein Shake",
            "calories_consumed": 320,
            "protein_g": 30,
            "carbs_g": 25,
            "fat_g": 8,
            "is_manual": True,
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["is_manual"] is True
    assert body["meal_id"] is None
    assert body["food_name"] == "Homemade Protein Shake"

    analytics = client.get(f"/users/{user_id}/analytics/today")
    assert analytics.status_code == 200
    assert analytics.json()["total_calories"] >= 320


def test_manual_food_log_rejects_empty_name(client):
    user_id = _register_user(client)

    res = client.post(
        f"/users/{user_id}/logs",
        json={
            "food_name": "   ",
            "calories_consumed": 200,
            "protein_g": 10,
            "carbs_g": 20,
            "fat_g": 5,
            "is_manual": True,
        },
    )
    assert res.status_code == 422


def test_manual_food_log_rejects_non_positive_values(client):
    user_id = _register_user(client)

    res = client.post(
        f"/users/{user_id}/logs",
        json={
            "food_name": "Snack",
            "calories_consumed": 100,
            "protein_g": 0,
            "carbs_g": 10,
            "fat_g": 5,
            "is_manual": True,
        },
    )
    assert res.status_code == 422


def test_ai_food_log_allows_zero_macros(client):
    user_id = _register_user(client)

    res = client.post(
        f"/users/{user_id}/logs",
        json={
            "food_name": "Apple",
            "calories_consumed": 52,
            "protein_g": 0,
            "carbs_g": 14,
            "fat_g": 0,
            "is_manual": False,
        },
    )
    assert res.status_code == 200
    assert res.json()["is_manual"] is False
