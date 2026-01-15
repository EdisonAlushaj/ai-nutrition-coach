# 🥑 AI Nutrition Coach - Simple Flow

Here is the simple explanation of how this project works.

## 🚦 The Flow: How data moves

Think of the **API Gateway** as the waiter in a restaurant. You (the user) only talk to the waiter, and the waiter talks to the chefs (the other services) for you.

| Step | You (User) 👤 | API Gateway (Waiter) 🤵 | The Service (Chef) 👩‍🍳 |
| :--- | :--- | :--- | :--- |
| **1. Register** | "I want to sign up!" | "Okay, I'll tell the User Manager." | **User Service:** Saves your name & password. |
| **2. Login** | "Here is my password." | "Checking with User Manager..." | **User Service:** "Yes, that's them!" |
| **3. Upload Photo** | "What food is this?" (Uploads Image) | "Hey Vision AI, what is this?" | **Food Recognition:** "It's a Pizza!" |
| **4. Get Info** | "Is Pizza healthy?" | "Hey Nutrition, tell me about Pizza." | **Nutrition Service:** "Pizza has 300 calories." |
| **5. Log It** | "I ate the Pizza." | "Logging, note this down." | **Logging Service:** Writes in your diary. |

---

## 🏗️ The Services (The Team)

Here is who does what in simple terms:

| Service Name | Nickname | What it does |
| :--- | :--- | :--- |
| **API Gateway** | The **Waiter** | Takes your orders and brings you results. You only talk to him. |
| **User Service** | The **Bouncer** | Handles sign-ups and makes sure you are who you say you are. |
| **Nutrition Service** | The **Librarian** | Knows everything about food (calories, protein, ingredients). |
| **Food Recognition** | The **Eyes** | Looks at pictures and guesses what food is inside. |
| **Logging Service** | The **Diary** | Remembers everything you ate so you don't have to. |
| **Database** | The **Vault** | Where all the information (users, logs, food data) is safely locked away. |

---

## 🚀 How to Start

Just run one command to act as the manager and wake everyone up:

```bash
docker compose up
```

Then go to this website to test it:
[http://localhost:8000/docs](http://localhost:8000/docs)
