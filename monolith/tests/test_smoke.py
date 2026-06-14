"""End-to-end smoke tests for the monolith.

These exercise the full request path (router -> crud -> shared DB) for each
domain in a single process, including the in-process user lookup that replaced
the old nutrition -> user-service HTTP call.
"""

PASSWORD = "password"
PROFILE = {
    "age": 30,
    "gender": "male",
    "height_cm": 180,
    "weight_kg": 75,
    "activity_level": "moderately_active",
    "goal": "lose_weight",
}

_email_counter = [0]


def _register_and_token(client):
    _email_counter[0] += 1
    email = f"smoke{_email_counter[0]}@example.com"
    res = client.post("/register", json={"email": email, "password": PASSWORD, "profile": PROFILE})
    assert res.status_code == 201, res.text
    body = res.json()
    return body["id"], body["access_token"], email


def test_register_login_and_me(client):
    user_id, token, email = _register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/users/me", headers=headers)
    assert me.status_code == 200
    me_body = me.json()
    assert me_body["email"] == email
    assert me_body["profile"]["goal"] == PROFILE["goal"]

    login = client.post("/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_non_admin_cannot_list_users(client):
    _, token, _ = _register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/admin/users", headers=headers).status_code == 403


def test_ingredient_meal_and_plan_flow(client):
    user_id, _, _ = _register_and_token(client)

    ing = client.post(
        "/admin/ingredients",
        json={
            "name": "Oats",
            "calories_per_100g": 380,
            "protein_per_100g": 13,
            "carbs_per_100g": 67,
            "fat_per_100g": 7,
        },
    )
    assert ing.status_code == 200
    ingredient_id = ing.json()["id"]

    meal = client.post(
        "/admin/meals",
        json={"name": "Oatmeal", "description": "bowl", "ingredient_ids": [ingredient_id]},
    )
    assert meal.status_code == 200
    assert meal.json()["total_calories"] == 380.0

    assert client.get("/meals").status_code == 200
    assert client.get(f"/meals/{meal.json()['id']}").status_code == 200
    assert client.get("/search-food", params={"name": "oat"}).status_code == 200

    # meal-plan exercises the in-process replacement of the old HTTP user lookup
    plan = client.get(f"/users/{user_id}/meal-plan")
    assert plan.status_code == 200
    assert len(plan.json()) >= 1


def test_logging_and_analytics(client):
    user_id, _, _ = _register_and_token(client)

    log = client.post(
        f"/users/{user_id}/logs",
        json={"food_name": "Oatmeal", "calories_consumed": 350, "protein_g": 12, "carbs_g": 60, "fat_g": 6},
    )
    assert log.status_code == 200

    assert client.get(f"/users/{user_id}/logs/").status_code == 200

    analytics = client.get(f"/users/{user_id}/analytics/today")
    assert analytics.status_code == 200
    assert analytics.json()["total_calories"] >= 350.0
