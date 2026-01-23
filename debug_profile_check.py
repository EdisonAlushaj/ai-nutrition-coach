import requests
import json

BASE_URL = "http://localhost:8000"

def register_and_check():
    # 1. Register a new user
    email = "testuser_profile@example.com"
    password = "password123"
    
    # Check if user exists or register
    print(f"--- Attempting to register {email} ---")
    reg_data = {
        "email": email,
        "password": password,
        "profile": {
            "age": 25,
            "gender": "male",
            "height_cm": 180,
            "weight_kg": 75,
            "activity_level": "moderately_active",
            "goal": "lose_weight"
        }
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/register", json=reg_data)
        if resp.status_code == 201:
            print("Registration successful.")
        elif resp.status_code == 400 and "already registered" in resp.text:
             print("User already exists, proceeding to login.")
        else:
             print(f"Registration failed: {resp.status_code} {resp.text}")
             # return
    except Exception as e:
        print(f"Registration error: {e}")
        return

    # 2. Login
    print(f"\n--- Logging in ---")
    login_data = {"email": email, "password": password}
    try:
        resp = requests.post(f"{BASE_URL}/login", json=login_data)
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            return
        
        token = resp.json()["access_token"]
        print("Login successful, token obtained.")
    except Exception as e:
         print(f"Login error: {e}")
         return

    # 3. Get Me
    print(f"\n--- Fetching /users/me ---")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
        print(f"Status: {resp.status_code}")
        try:
            data = resp.json()
            print(json.dumps(data, indent=2))
            
            if "profile" in data and data["profile"] and "goal" in data["profile"]:
                print("\nSUCCESS: Profile and goal found in response.")
                user_id = data.get("id")
                print(f"User ID from profile: {user_id}")
                
                 # 4. Get Meal Plan
                print(f"\n--- Fetching /users/{user_id}/meal-plan ---")
                try:
                    resp = requests.get(f"{BASE_URL}/users/{user_id}/meal-plan", headers=headers)
                    print(f"Status: {resp.status_code}")
                    if resp.status_code == 200:
                        meals = resp.json()
                        print(f"Meals found: {len(meals)}")
                        if len(meals) > 0:
                            print(json.dumps(meals[0], indent=2))
                    else:
                        print(f"Failed to fetch meal plan: {resp.text}")
                except Exception as e:
                    print(f"Meal plan fetch error: {e}")

            else:
                 print("\nFAILURE: Profile or goal MISSING in response.")
                 
        except:
            print(f"Response text: {resp.text}")
            
    except Exception as e:
        print(f"Fetch error: {e}")

if __name__ == "__main__":
    if requests.get(f"{BASE_URL}/").status_code == 200:
         register_and_check()
    else:
        print("API Gateway appears to be down.")
