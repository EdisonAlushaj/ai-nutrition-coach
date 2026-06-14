"""Tests for target weight (US 5.3)."""

from tests.test_smoke import PASSWORD, PROFILE

_email_counter = [900]


def _register_and_token(client):
    _email_counter[0] += 1
    email = f"targetweight{_email_counter[0]}@example.com"
    res = client.post(
        "/register",
        json={"email": email, "password": PASSWORD, "profile": PROFILE},
    )
    assert res.status_code == 201, res.text
    return res.json()["id"], res.json()["access_token"]


def test_set_target_weight_on_profile(client):
    user_id, token = _register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.put(
        "/users/me/profile",
        headers=headers,
        json={
            "first_name": None,
            "last_name": None,
            "age": 30,
            "gender": "male",
            "height_cm": 180,
            "weight_kg": 75,
            "target_weight_kg": 70,
            "activity_level": "moderately_active",
            "goal": "lose_weight",
        },
    )
    assert res.status_code == 200, res.text
    assert res.json()["target_weight_kg"] == 70


def test_nutrition_goals_includes_target_weight(client):
    user_id, token = _register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client.put(
        "/users/me/profile",
        headers=headers,
        json={
            "first_name": None,
            "last_name": None,
            "age": 30,
            "gender": "male",
            "height_cm": 180,
            "weight_kg": 75,
            "target_weight_kg": 68,
            "activity_level": "moderately_active",
            "goal": "lose_weight",
        },
    )

    res = client.get(f"/users/{user_id}/nutrition-goals")
    assert res.status_code == 200
    body = res.json()
    assert body["current_weight_kg"] == 75
    assert body["target_weight_kg"] == 68
