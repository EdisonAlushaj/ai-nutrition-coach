import requests
import random
import string
import sys

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def verify_registration_login():
    email = f"test_{get_random_string(8)}@example.com"
    password = "password123"
    
    url = "http://localhost:8004/users/"
    data = {
        "email": email,
        "password": password,
        "profile": {
            "age": 25,
            "gender": "male",
            "height_cm": 180,
            "weight_kg": 75,
            "activity_level": "moderately_active",
            "goal": "maintain"
        }
    }
    
    print(f"Registering user: {email}")
    try:
        response = requests.post(url, json=data)
        
        if response.status_code != 200:
            print(f"FAILED: Registration failed with status {response.status_code}")
            print(response.text)
            sys.exit(1)
            
        json_resp = response.json()
        
        # Check tokens in body
        if "access_token" not in json_resp:
            print("FAILED: access_token not found in response body")
            sys.exit(1)
        
        if "refresh_token" not in json_resp:
            print("FAILED: refresh_token not found in response body")
            sys.exit(1)
            
        # Check user data in body
        if "email" not in json_resp or json_resp["email"] != email:
            print("FAILED: User email missing or incorrect in response")
            sys.exit(1)
            
        # Check cookies
        cookies = response.cookies
        if "access_token" not in cookies:
            print("FAILED: access_token cookie not set")
            sys.exit(1)
            
        if "refresh_token" not in cookies:
            print("FAILED: refresh_token cookie not set")
            sys.exit(1)
            
        print("SUCCESS: Registration returned tokens and set cookies!")
        
    except requests.exceptions.ConnectionError:
        print("FAILED: Could not connect to server. Is it running?")
        sys.exit(1)
    except Exception as e:
        print(f"FAILED: An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_registration_login()
