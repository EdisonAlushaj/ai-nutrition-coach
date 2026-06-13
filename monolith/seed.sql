INSERT INTO ingredients (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g) VALUES
('Beef Patty', 250, 20, 0, 18),
('Buns', 260, 8, 50, 3),
('Cheese', 400, 25, 1, 33),
('Tomato', 18, 0.9, 3.9, 0.2),
('Lettuce', 15, 1.4, 2.9, 0.2),
('Pizza Dough', 270, 8, 55, 1),
('Mozzarella', 280, 22, 2, 20),
('Tomato Sauce', 40, 1.5, 8, 0.2),
('Pepperoni', 490, 23, 1, 44),
('Chicken Breast', 165, 31, 0, 3.6),
('Rice', 130, 2.7, 28, 0.3),
('Broccoli', 34, 2.8, 7, 0.4),
('Apple', 52, 0.3, 14, 0.2),
('Banana', 89, 1.1, 23, 0.3),
('Pomegranate', 83, 1.7, 19, 1.2),
('Fig', 74, 0.8, 19, 0.3)
ON CONFLICT (name) DO NOTHING;

INSERT INTO meals (name, description, total_calories, protein_g, carbs_g, fat_g) VALUES
('Cheeseburger', 'Classic beef burger with cheese', 600, 35, 45, 30),
('Pizza Pepperoni', 'Delicious pepperoni pizza', 850, 35, 90, 40),
('Chicken Rice Bowl', 'Healthy chicken and rice with broccoli', 450, 40, 60, 10),
('Apple', 'A fresh red apple', 52, 0, 14, 0),
('Banana', 'A ripe yellow banana', 89, 1, 23, 0),
('Pomegranate', 'Fresh pomegranate seeds', 83, 1.7, 19, 1.2),
('Fig', 'A sweet fresh fig', 74, 0.8, 19, 0.3),
('Pepperoni Pizza Slice', 'Single slice of pepperoni pizza', 300, 12, 30, 15)
ON CONFLICT DO NOTHING;

-- Link Cheeseburger ingredients
INSERT INTO meal_ingredients (meal_id, ingredient_id)
SELECT m.id, i.id FROM meals m, ingredients i 
WHERE m.name = 'Cheeseburger' AND i.name IN ('Beef Patty', 'Buns', 'Cheese', 'Tomato', 'Lettuce')
ON CONFLICT DO NOTHING;

-- Link Pizza Pepperoni ingredients
INSERT INTO meal_ingredients (meal_id, ingredient_id)
SELECT m.id, i.id FROM meals m, ingredients i 
WHERE m.name = 'Pizza Pepperoni' AND i.name IN ('Pizza Dough', 'Mozzarella', 'Tomato Sauce', 'Pepperoni')
ON CONFLICT DO NOTHING;

-- Link Chicken Rice Bowl ingredients
INSERT INTO meal_ingredients (meal_id, ingredient_id)
SELECT m.id, i.id FROM meals m, ingredients i 
WHERE m.name = 'Chicken Rice Bowl' AND i.name IN ('Chicken Breast', 'Rice', 'Broccoli')
ON CONFLICT DO NOTHING;

-- Link Apple
INSERT INTO meal_ingredients (meal_id, ingredient_id)
SELECT m.id, i.id FROM meals m, ingredients i 
WHERE m.name = 'Apple' AND i.name = 'Apple'
ON CONFLICT DO NOTHING;

-- Link Banana
INSERT INTO meal_ingredients (meal_id, ingredient_id)
SELECT m.id, i.id FROM meals m, ingredients i 
WHERE m.name = 'Banana' AND i.name = 'Banana'
ON CONFLICT DO NOTHING;

-- Link Pomegranate
INSERT INTO meal_ingredients (meal_id, ingredient_id)
SELECT m.id, i.id FROM meals m, ingredients i 
WHERE m.name = 'Pomegranate' AND i.name = 'Pomegranate'
ON CONFLICT DO NOTHING;

-- Link Fig
INSERT INTO meal_ingredients (meal_id, ingredient_id)
SELECT m.id, i.id FROM meals m, ingredients i 
WHERE m.name = 'Fig' AND i.name = 'Fig'
ON CONFLICT DO NOTHING;
