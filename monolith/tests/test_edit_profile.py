"""Tests for edit profile (US 5.1)."""

from tests.test_smoke import PASSWORD, PROFILE

_email_counter = [800]


def _register_and_token(client):
    _email_counter[0] += 1
    email = f"editprofile{_email_counter[0]}@example.com"
    res = client.post(
        "/register",
        json={"email": email, "password": PASSWORD, "profile": PROFILE},
    )
    assert res.status_code == 201, res.text
    return res.json()["access_token"]


def _update_payload(**overrides):
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "age": 31,
        "gender": "male",
        "height_cm": 181,
        "weight_kg": 74,
        "target_weight_kg": 70,
        "activity_level": "very_active",
        "goal": "gain_muscle",
    }
    payload.update(overrides)
    return payload


def test_update_profile_success(client):
    token = _register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.put("/users/me/profile", headers=headers, json=_update_payload())
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["first_name"] == "John"
    assert body["last_name"] == "Doe"
    assert body["age"] == 31
    assert body["goal"] == "gain_muscle"
    assert body["weight_kg"] == 74
    assert body["target_weight_kg"] == 70

    me = client.get("/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["profile"]["first_name"] == "John"


def test_update_profile_validation(client):
    token = _register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.put(
        "/users/me/profile",
        headers=headers,
        json=_update_payload(weight_kg=0),
    )
    assert res.status_code == 422


def test_update_profile_requires_auth(client):
    res = client.put("/users/me/profile", json=_update_payload())
    assert res.status_code == 401
