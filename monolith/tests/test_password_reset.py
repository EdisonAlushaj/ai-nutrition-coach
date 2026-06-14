"""Tests for forgot / reset password flow (US 1.4)."""

from unittest.mock import patch

from tests.test_smoke import PASSWORD, PROFILE

_email_counter = [100]


def _register_user(client):
    _email_counter[0] += 1
    email = f"reset{_email_counter[0]}@example.com"
    res = client.post(
        "/register",
        json={"email": email, "password": PASSWORD, "profile": PROFILE},
    )
    assert res.status_code == 201, res.text
    return email


def test_forgot_password_always_returns_generic_message(client):
    known_email = _register_user(client)
    unknown_email = "missing-user@example.com"

    known = client.post("/auth/forgot-password", json={"email": known_email})
    unknown = client.post("/auth/forgot-password", json={"email": unknown_email})

    assert known.status_code == 200
    assert unknown.status_code == 200
    assert known.json()["message"] == unknown.json()["message"]


def test_forgot_password_invalid_email_format(client):
    res = client.post("/auth/forgot-password", json={"email": "not-an-email"})
    assert res.status_code == 422


@patch("app.users.router.send_password_reset_email")
def test_reset_password_and_login(mock_send_email, client):
    email = _register_user(client)
    captured = {}

    def capture_email(to_email, token):
        captured["email"] = to_email
        captured["token"] = token

    mock_send_email.side_effect = capture_email

    forgot = client.post("/auth/forgot-password", json={"email": email})
    assert forgot.status_code == 200
    mock_send_email.assert_called_once()
    assert captured["email"] == email
    token = captured["token"]

    validate = client.get("/auth/reset-password/validate", params={"token": token})
    assert validate.status_code == 200

    new_password = "newpass123"
    reset = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": new_password,
            "confirm_password": new_password,
        },
    )
    assert reset.status_code == 200

    old_login = client.post("/login", json={"email": email, "password": PASSWORD})
    assert old_login.status_code == 401

    new_login = client.post("/login", json={"email": email, "password": new_password})
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()


def test_reset_password_rejects_reused_token(client):
    email = _register_user(client)

    with patch("app.users.router.send_password_reset_email") as mock_send:
        token_box = {}

        def capture(_, token):
            token_box["token"] = token

        mock_send.side_effect = capture
        client.post("/auth/forgot-password", json={"email": email})
        token = token_box["token"]

    payload = {
        "token": token,
        "new_password": "another123",
        "confirm_password": "another123",
    }
    assert client.post("/auth/reset-password", json=payload).status_code == 200
    assert client.post("/auth/reset-password", json=payload).status_code == 400


def test_reset_password_rejects_weak_password(client):
    email = _register_user(client)

    with patch("app.users.router.send_password_reset_email") as mock_send:
        token_box = {}

        def capture(_, token):
            token_box["token"] = token

        mock_send.side_effect = capture
        client.post("/auth/forgot-password", json={"email": email})
        token = token_box["token"]

    res = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": "short1",
            "confirm_password": "short1",
        },
    )
    assert res.status_code == 400
