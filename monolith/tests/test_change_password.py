"""Tests for change password while logged in (US 5.2)."""

from tests.test_smoke import PASSWORD, PROFILE

_email_counter = [200]


def _register_and_token(client):
    _email_counter[0] += 1
    email = f"changepw{_email_counter[0]}@example.com"
    res = client.post(
        "/register",
        json={"email": email, "password": PASSWORD, "profile": PROFILE},
    )
    assert res.status_code == 201, res.text
    return email, res.json()["access_token"]


def test_change_password_success(client):
    email, token = _register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    new_password = "newpass123"

    res = client.post(
        "/users/me/change-password",
        headers=headers,
        json={
            "current_password": PASSWORD,
            "new_password": new_password,
            "confirm_password": new_password,
        },
    )
    assert res.status_code == 200

    assert client.post("/login", json={"email": email, "password": PASSWORD}).status_code == 401
    assert client.post("/login", json={"email": email, "password": new_password}).status_code == 200


def test_change_password_wrong_current(client):
    _, token = _register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/users/me/change-password",
        headers=headers,
        json={
            "current_password": "wrongpass1",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        },
    )
    assert res.status_code == 400
    assert "incorrect" in res.json()["detail"].lower()


def test_change_password_mismatch_confirm(client):
    _, token = _register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/users/me/change-password",
        headers=headers,
        json={
            "current_password": PASSWORD,
            "new_password": "newpass123",
            "confirm_password": "different1",
        },
    )
    assert res.status_code == 422


def test_change_password_weak_new_password(client):
    _, token = _register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/users/me/change-password",
        headers=headers,
        json={
            "current_password": PASSWORD,
            "new_password": "short1",
            "confirm_password": "short1",
        },
    )
    assert res.status_code == 400


def test_change_password_requires_auth(client):
    res = client.post(
        "/users/me/change-password",
        json={
            "current_password": PASSWORD,
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        },
    )
    assert res.status_code == 401
