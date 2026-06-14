"""Tests for motivation quotes (Epic 4)."""

from datetime import date

from app.motivation import service
from app.motivation.quotes import QUOTES_BY_GOAL
from tests.test_smoke import PASSWORD, PROFILE

_email_counter = [1000]


def _register_user(client):
    _email_counter[0] += 1
    email = f"motivation{_email_counter[0]}@example.com"
    res = client.post(
        "/register",
        json={"email": email, "password": PASSWORD, "profile": PROFILE},
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_daily_quote_is_stable_for_same_day(client):
    user_id = _register_user(client)

    first = client.get(f"/users/{user_id}/motivation/daily")
    second = client.get(f"/users/{user_id}/motivation/daily")
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["message"] == second.json()["message"]
    assert first.json()["category"] == "lose_weight"
    assert first.json()["is_daily"] is True


def test_daily_quote_uses_goal_category(client):
    user_id = _register_user(client)

    res = client.get(f"/users/{user_id}/motivation/daily")
    assert res.status_code == 200
    assert res.json()["category"] == "lose_weight"
    assert res.json()["message"] in QUOTES_BY_GOAL["lose_weight"]


def test_random_quote_endpoint(client):
    user_id = _register_user(client)

    daily = client.get(f"/users/{user_id}/motivation/daily").json()
    res = client.get(
        f"/users/{user_id}/motivation/random",
        params={"exclude": daily["message"]},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["is_daily"] is False
    assert body["message"] in QUOTES_BY_GOAL["lose_weight"]


def test_daily_quote_changes_by_date():
    quote_day_one = service.get_daily_quote(user_id=1, category="maintain", query_date=date(2026, 6, 1))
    quote_day_two = service.get_daily_quote(user_id=1, category="maintain", query_date=date(2026, 6, 2))
    assert quote_day_one.message != quote_day_two.message or len(QUOTES_BY_GOAL["maintain"]) == 1


def test_fallback_when_unknown_category():
    quote = service.get_daily_quote(user_id=1, category="unknown", query_date=date.today())
    assert quote.category == "unknown"
    assert quote.message
