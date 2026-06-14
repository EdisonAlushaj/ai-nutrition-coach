"""Generate monolith/seed_full.sql with schema-correct PostgreSQL types."""

from __future__ import annotations

import random

# Verified in running monolith container for password "password123"
BCRYPT_PASSWORD123 = "$2b$12$Djmv3opCkroKRBlMeD9n7eqBJhVAC3A4KdjQki8v.5Hms0tAQWvw2"

ingredients_data = [
    ("Chicken Breast", 165, 31, 0, 3.6),
    ("Salmon", 208, 20, 0, 13),
    ("White Rice", 130, 2.7, 28, 0.3),
    ("Brown Rice", 112, 2.6, 23, 0.9),
    ("Eggs", 155, 13, 1.1, 11),
    ("Oats", 389, 16.9, 66.3, 6.9),
    ("Avocado", 160, 2, 8.5, 14.7),
    ("Olive Oil", 884, 0, 0, 100),
    ("Sweet Potato", 86, 1.6, 20, 0.1),
    ("Broccoli", 34, 2.8, 7, 0.4),
    ("Spinach", 23, 2.9, 3.6, 0.4),
    ("Greek Yogurt", 59, 10, 3.6, 0.4),
    ("Almonds", 579, 21, 22, 50),
    ("Banana", 89, 1.1, 23, 0.3),
    ("Apple", 52, 0.3, 14, 0.2),
    ("Peanut Butter", 588, 25, 20, 50),
    ("Whey Protein", 400, 80, 6, 6),
    ("Beef Patty", 250, 20, 0, 18),
    ("Tuna canned", 116, 26, 0, 1),
    ("Whole Wheat Bread", 247, 13, 41, 3.4),
    ("Quinoa", 120, 4.4, 21.3, 1.9),
    ("Cottage Cheese", 98, 11, 3.4, 4.3),
    ("Black Beans", 132, 8.9, 23.7, 0.5),
    ("Mixed Berries", 50, 1, 12, 0.5),
    ("Honey", 304, 0.3, 82.4, 0),
]

meals_data = [
    ("Grilled Chicken and Rice", "Classic bodybuilding meal with chicken breast and white rice.", 460, 49.3, 42, 6.1, ["Chicken Breast", "White Rice", "Olive Oil"]),
    ("Oatmeal Protein Bowl", "Oatmeal cooked with whey protein and topped with banana.", 578, 38.0, 78.3, 9.9, ["Oats", "Whey Protein", "Banana"]),
    ("Salmon and Sweet Potato", "Baked salmon paired with sweet potato and broccoli.", 546, 34.4, 47.0, 23.9, ["Salmon", "Sweet Potato", "Broccoli"]),
    ("Avocado Toast with Eggs", "Whole wheat toast with mashed avocado and fried eggs.", 467, 19.0, 32.6, 29.1, ["Whole Wheat Bread", "Avocado", "Eggs"]),
    ("Greek Yogurt Berry Mix", "High protein snack with Greek yogurt, honey, and berries.", 218, 20.6, 32.4, 1.3, ["Greek Yogurt", "Mixed Berries", "Honey"]),
    ("Protein Shake", "Post-workout whey protein shake with milk or water.", 140, 24.0, 1.8, 1.8, ["Whey Protein"]),
    ("Tuna Salad Sandwich", "Canned tuna mixed with light dressing on whole wheat bread.", 379, 31.2, 44.4, 4.7, ["Tuna canned", "Whole Wheat Bread"]),
    ("Beef and Broccoli", "Stir-fried beef patty strips with broccoli and brown rice.", 624, 45.4, 53.0, 22.8, ["Beef Patty", "Broccoli", "Brown Rice"]),
    ("Scrambled Eggs and Spinach", "Quick breakfast with 3 eggs and fresh spinach leaves.", 241, 20.9, 2.5, 16.7, ["Eggs", "Spinach"]),
    ("Quinoa Salad with Avocado", "Nutritious quinoa base with avocado and black beans.", 412, 15.3, 53.5, 17.1, ["Quinoa", "Avocado", "Black Beans"]),
    ("Peanut Butter Banana Toast", "Whole wheat bread with peanut butter and banana slices.", 440, 15.1, 51.5, 20.3, ["Whole Wheat Bread", "Peanut Butter", "Banana"]),
    ("Cottage Cheese Bowl", "Low fat cottage cheese mixed with honey and almonds.", 361, 24.1, 21.0, 19.3, ["Cottage Cheese", "Honey", "Almonds"]),
    ("Black Beans and Rice", "Simple vegan source of complete protein.", 374, 14.3, 73.7, 1.1, ["Black Beans", "White Rice"]),
    ("Chicken Spinach Salad", "Grilled chicken breast over a bed of spinach and olive oil.", 322, 32.2, 1.4, 18.8, ["Chicken Breast", "Spinach", "Olive Oil"]),
    ("Berry Protein Oats", "Oatmeal bowl with mixed berries and whey protein.", 489, 37.9, 64.3, 7.2, ["Oats", "Mixed Berries", "Whey Protein"]),
    ("Almond Snack Pack", "A handful of raw almonds for clean fats.", 174, 6.3, 6.6, 15.0, ["Almonds"]),
    ("Egg Rice Bowl", "Fried eggs over white rice with a touch of olive oil.", 469, 18.4, 42.0, 21.6, ["Eggs", "White Rice", "Olive Oil"]),
    ("Salmon Salad", "Flaked salmon over spinach with olive oil drizzle.", 343, 21.2, 1.4, 28.1, ["Salmon", "Spinach", "Olive Oil"]),
    ("Sweet Potato Mash with Beef", "Beef patty served with a side of sweet potato mash.", 586, 23.2, 40.0, 18.2, ["Beef Patty", "Sweet Potato"]),
    ("Chicken Quinoa Bowl", "Lean chicken breast mixed with nutrient-dense quinoa.", 450, 44.2, 42.6, 8.4, ["Chicken Breast", "Quinoa"]),
    ("Tuna Quinoa Plate", "Canned tuna over seasoned quinoa and broccoli.", 404, 39.2, 49.6, 4.3, ["Tuna canned", "Quinoa", "Broccoli"]),
    ("Healthy Burger Plate", "Beef patty served over a bed of spinach and sliced avocado.", 433, 24.9, 12.1, 33.1, ["Beef Patty", "Spinach", "Avocado"]),
    ("Yogurt Oatmeal Parfait", "Layered Greek yogurt, oats, and honey.", 352, 21.7, 59.1, 1.8, ["Greek Yogurt", "Oats", "Honey"]),
    ("Scrambled Egg Plate", "Simple plain scrambled eggs cooked without oil.", 155, 13.0, 1.1, 11.0, ["Eggs"]),
    ("Honey Glazed Salmon", "Pan-seared salmon finished with a touch of pure honey.", 339, 20.1, 16.5, 13.0, ["Salmon", "Honey"]),
]

log_entries = [
    ("demo1@example.com", "Grilled Chicken and Rice", "2026-06-01 08:30:00+02"),
    ("demo1@example.com", "Oatmeal Protein Bowl", "2026-06-01 13:15:00+02"),
    ("demo1@example.com", "Salmon and Sweet Potato", "2026-06-01 19:45:00+02"),
    ("demo2@example.com", "Avocado Toast with Eggs", "2026-06-02 09:00:00+02"),
    ("demo2@example.com", "Protein Shake", "2026-06-02 11:30:00+02"),
    ("demo2@example.com", "Tuna Salad Sandwich", "2026-06-02 14:00:00+02"),
    ("demo2@example.com", "Beef and Broccoli", "2026-06-02 20:00:00+02"),
    ("demo3@example.com", "Scrambled Eggs and Spinach", "2026-06-03 07:30:00+02"),
    ("demo3@example.com", "Greek Yogurt Berry Mix", "2026-06-03 10:15:00+02"),
    ("demo3@example.com", "Quinoa Salad with Avocado", "2026-06-03 13:30:00+02"),
    ("demo3@example.com", "Chicken Spinach Salad", "2026-06-03 19:00:00+02"),
    ("demo4@example.com", "Peanut Butter Banana Toast", "2026-06-04 08:00:00+02"),
    ("demo4@example.com", "Cottage Cheese Bowl", "2026-06-04 12:00:00+02"),
    ("demo4@example.com", "Berry Protein Oats", "2026-06-04 16:30:00+02"),
    ("demo5@example.com", "Black Beans and Rice", "2026-06-05 12:30:00+02"),
    ("demo5@example.com", "Almond Snack Pack", "2026-06-05 15:00:00+02"),
    ("demo5@example.com", "Egg Rice Bowl", "2026-06-05 19:30:00+02"),
    ("demo6@example.com", "Salmon Salad", "2026-06-06 13:00:00+02"),
    ("demo6@example.com", "Sweet Potato Mash with Beef", "2026-06-06 20:15:00+02"),
    ("demo7@example.com", "Chicken Quinoa Bowl", "2026-06-07 12:00:00+02"),
    ("demo7@example.com", "Tuna Quinoa Plate", "2026-06-07 18:30:00+02"),
    ("demo8@example.com", "Healthy Burger Plate", "2026-06-08 13:15:00+02"),
    ("demo8@example.com", "Yogurt Oatmeal Parfait", "2026-06-08 08:30:00+02"),
    ("demo9@example.com", "Scrambled Egg Plate", "2026-06-09 07:00:00+02"),
    ("demo9@example.com", "Honey Glazed Salmon", "2026-06-09 20:00:00+02"),
]

def q(value: str) -> str:
    return value.replace("'", "''")


def main() -> None:
    sql: list[str] = ["BEGIN;"]

    ing_values = ", ".join(
        f"('{q(name)}', {cal}, {protein}, {carbs}, {fat})"
        for name, cal, protein, carbs, fat in ingredients_data
    )
    sql.append("-- Seed ingredients")
    sql.append(
        "INSERT INTO ingredients (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g) "
        f"VALUES {ing_values} ON CONFLICT (name) DO NOTHING;"
    )

    sql.append("\n-- Seed meals and meal_ingredients")
    for name, desc, cal, protein, carbs, fat, ings in meals_data:
        sql.append(
            "INSERT INTO meals (name, description, total_calories, protein_g, carbs_g, fat_g) "
            f"SELECT '{q(name)}', '{q(desc)}', {cal}, {protein}, {carbs}, {fat} "
            f"WHERE NOT EXISTS (SELECT 1 FROM meals WHERE name = '{q(name)}');"
        )
        ing_list = ", ".join(f"'{q(i)}'" for i in ings)
        sql.append(
            "INSERT INTO meal_ingredients (meal_id, ingredient_id) "
            "SELECT m.id, i.id FROM meals m JOIN ingredients i ON i.name IN ("
            f"{ing_list}) WHERE m.name = '{q(name)}' ON CONFLICT DO NOTHING;"
        )

    sql.append("\n-- Seed users (password for demo accounts: password123)")
    for i in range(1, 21):
        email = f"demo{i}@example.com"
        role = "admin" if i in (1, 2) else "user"
        sql.append(
            "INSERT INTO users (email, hashed_password, is_active, role) "
            f"VALUES ('{email}', '{BCRYPT_PASSWORD123}', true, '{role}'::roleenum) "
            "ON CONFLICT (email) DO NOTHING;"
        )

    random.seed(42)
    genders = ["male", "female"]
    activity_levels = [
        "sedentary",
        "lightly_active",
        "moderately_active",
        "very_active",
        "extra_active",
    ]
    goals = ["lose_weight", "maintain", "gain_muscle"]

    sql.append("\n-- Seed profiles")
    for i in range(1, 21):
        email = f"demo{i}@example.com"
        age = random.randint(22, 50)
        gender = genders[i % 2]
        height = round(random.uniform(160.0, 190.0), 1)
        weight = round(random.uniform(55.0, 95.0), 1)
        activity = activity_levels[i % len(activity_levels)]
        goal = goals[i % len(goals)]
        sql.append(
            "INSERT INTO profiles (user_id, age, gender, height_cm, weight_kg, activity_level, goal) "
            f"SELECT u.id, {age}, '{gender}'::genderenum, {height}, {weight}, "
            f"'{activity}'::activitylevelenum, '{goal}'::goalenum "
            f"FROM users u WHERE u.email = '{email}' "
            "AND NOT EXISTS (SELECT 1 FROM profiles p WHERE p.user_id = u.id);"
        )

    sql.append("\n-- Seed food_logs")
    for email, meal_name, timestamp in log_entries:
        meal = next(m for m in meals_data if m[0] == meal_name)
        _, _, cal, protein, carbs, fat, _ = meal
        sql.append(
            "INSERT INTO food_logs (user_id, meal_id, food_name, calories_consumed, protein_g, carbs_g, fat_g, timestamp) "
            f"SELECT u.id, m.id, '{q(meal_name)}', {cal}, {protein}, {carbs}, {fat}, '{timestamp}'::timestamptz "
            f"FROM users u JOIN meals m ON m.name = '{q(meal_name)}' "
            f"WHERE u.email = '{email}' "
            f"AND NOT EXISTS (SELECT 1 FROM food_logs fl WHERE fl.user_id = u.id AND fl.timestamp = '{timestamp}'::timestamptz);"
        )

    sql.append("\n-- Seed daily_analytics from food_logs")
    sql.append(
        "INSERT INTO daily_analytics (user_id, date, total_calories, total_protein, total_carbs, total_fat) "
        "SELECT agg.user_id, agg.log_date, agg.total_calories, agg.total_protein, agg.total_carbs, agg.total_fat "
        "FROM ( "
        "  SELECT user_id, timestamp::date AS log_date, "
        "         SUM(calories_consumed) AS total_calories, "
        "         SUM(protein_g) AS total_protein, "
        "         SUM(carbs_g) AS total_carbs, "
        "         SUM(fat_g) AS total_fat "
        "  FROM food_logs "
        "  GROUP BY user_id, timestamp::date "
        ") agg "
        "WHERE NOT EXISTS ( "
        "  SELECT 1 FROM daily_analytics da "
        "  WHERE da.user_id = agg.user_id AND da.date = agg.log_date "
        ");"
    )

    sql.append("COMMIT;")

    output_path = __file__.replace("build_seed_full.py", "seed_full.sql")
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(sql) + "\n")

    print(f"Wrote {output_path} ({len(sql)} statements blocks)")


if __name__ == "__main__":
    main()
