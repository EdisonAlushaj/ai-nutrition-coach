"""Tests for barcode food lookup (US 3.5)."""

from tests.test_smoke import PASSWORD, PROFILE

_email_counter = [1100]


def _register_user(client):
    _email_counter[0] += 1
    email = f"barcode{_email_counter[0]}@example.com"
    res = client.post(
        "/register",
        json={"email": email, "password": PASSWORD, "profile": PROFILE},
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_lookup_local_barcode(client):
    res = client.get("/foods/barcode/1234567890123")
    assert res.status_code == 200
    body = res.json()
    assert body["food_name"] == "Demo Protein Bar"
    assert body["calories_consumed"] == 220
    assert body["source"] == "local"


def test_lookup_unknown_barcode(client):
    res = client.get("/foods/barcode/9999999999999")
    assert res.status_code == 404


def test_log_scanned_barcode_food(client):
    user_id = _register_user(client)

    lookup = client.get("/foods/barcode/4001686341234")
    assert lookup.status_code == 200
    food = lookup.json()

    log = client.post(
        f"/users/{user_id}/logs",
        json={
            "food_name": food["food_name"],
            "calories_consumed": food["calories_consumed"],
            "protein_g": food["protein_g"],
            "carbs_g": food["carbs_g"],
            "fat_g": food["fat_g"],
            "is_manual": False,
        },
    )
    assert log.status_code == 200
    assert log.json()["food_name"] == "Greek Yogurt Cup"

    analytics = client.get(f"/users/{user_id}/analytics/today")
    assert analytics.json()["total_calories"] >= 120
