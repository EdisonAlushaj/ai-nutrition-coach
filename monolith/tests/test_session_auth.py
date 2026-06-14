"""Tests for HttpOnly cookie session auth (US 1.3)."""

from tests.test_smoke import PASSWORD, PROFILE

_email_counter = [1200]


def _register_user(client):
    _email_counter[0] += 1
    email = f"session{_email_counter[0]}@example.com"
    res = client.post(
        "/register",
        json={"email": email, "password": PASSWORD, "profile": PROFILE},
    )
    assert res.status_code == 201, res.text
    return email, res.json()["access_token"]


def test_users_me_with_session_cookie(client):
    email, _ = _register_user(client)

    me = client.get("/users/me")
    assert me.status_code == 200
    assert me.json()["email"] == email


def test_users_me_still_accepts_bearer_token(client):
    _, token = _register_user(client)
    client.cookies.clear()

    me = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200


def test_refresh_session_issues_new_access_cookie(client):
    _register_user(client)

    res = client.post("/auth/refresh")
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert client.get("/users/me").status_code == 200


def test_logout_clears_session(client):
    _register_user(client)
    assert client.get("/users/me").status_code == 200

    logout = client.post("/auth/logout")
    assert logout.status_code == 200

    assert client.get("/users/me").status_code == 401
