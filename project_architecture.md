# AI Nutrition Coach - Project Architecture & Flow

This document outlines the architecture of the AI Nutrition Coach application, explaining how the services interact, what they do, and how data flows through the system.

## 1. High-Level Architecture

The project is built as a **Microservices Architecture**, orchestrated using **Docker Compose**. 

There is a central **API Gateway** that acts as the single entry point for all client requests. It routes traffic to the appropriate backend services.

### Core Services:
1.  **API Gateway** (`api-gateway`) - Port `8000`
2.  **User Service** (`user-service`) - Port `8001`
3.  **Nutrition Service** (`nutrition-service`) - Port `8002`
4.  **Logging & Analytics Service** (`logging-analytics-service`) - Port `8003`
5.  **Food Recognition Service** (`food-recognition-service`) - Port `8004`
6.  **Database** (`db`) - PostgreSQL Instance (Port `5432`)

---

## 2. What Each Service Does

### 🌐 API Gateway (`api_gateway`)
- **Role:** The "Front Door" of the application.
- **Responsibility:** Receives all requests from the user (frontend/mobile app), performs routing, and sometimes aggregates responses. It does not store business data itself but forwards requests to the specialized services.
- **Key Endpoints:**
    - `/register`: For creating new users.
    - `/recognize-food`: Uploads an image to recognize food.
    - `/meals`: Fetches nutrition data.
    - `/users/{id}/logs`: Logs food intake.

### 👤 User Service (`user_service`)
- **Role:** Identity Provider.
- **Responsibility:** Manages user registration, profiles, and potentially authentication tokens (though simple registration is visible currently).
- **Database:** Stores user accounts.

### 🍎 Nutrition Service (`nutrition_service`)
- **Role:** Dietician.
- **Responsibility:** 
    - Manages the database of food items/meals (calories, proteins, fats, etc.).
    - Generates or retrieves meal plans.
    - Searches for food items.
- **Database:** Stores food items and meal plans.

### 📊 Logging & Analytics Service (`logging_analytics_service`)
- **Role:** Diary & Analyst.
- **Responsibility:** 
    - Records what users eat (logs).
    - Can potentially calculate daily totals or analyze trends.
- **Database:** Stores user food logs.

### 📸 Food Recognition Service (`food_recognition_service`)
- **Role:** AI Vision.
- **Responsibility:** 
    - Takes an image file as input.
    - Uses a Machine Learning model to predict what food is in the image.
    - Returns the prediction (e.g., "Pizza", "Apple").

---

## 3. How It Works (The Flow)

Here are a few example user flows to illustrate how the system communicates.

### Scenario A: User Registers
1.  **User** sends `POST /register` to **API Gateway** (Port 8000).
2.  **API Gateway** forwards the request to **User Service** (Port 8001).
3.  **User Service** saves the user to **PostgreSQL**.
4.  **User Service** responds with success.
5.  **API Gateway** returns the success message to the **User**.

### Scenario B: User Uploads a Meal Photo
1.  **User** sends `POST /recognize-food` with an image to **API Gateway**.
2.  **API Gateway** forwards the image to **Food Recognition Service** (Port 8004).
3.  **Food Recognition Service** processes the image and predicts "Hamburger".
4.  **Food Recognition Service** returns the prediction "Hamburger".
5.  **API Gateway** returns "Hamburger" to the **User**.

### Scenario C: User Logs a Meal
1.  **User** sends `POST /users/{id}/logs` (e.g., "I ate a Hamburger") to **API Gateway**.
2.  **API Gateway** forwards the data to **Logging Service** (Port 8003).
3.  **Logging Service** saves the entry to **PostgreSQL**.
4.  **API Gateway** confirms the log was saved.

---

## 4. How to Use It (Development)

The system is containerized, so you run it using Docker.

1.  **Start the System:**
    ```bash
    docker compose up --build
    ```
    This spins up all 5 containers and the database.

2.  **Access the API:**
    - Open your browser to: `http://localhost:8000/docs`
    - This is the **Swagger UI** (Documentation) provided by the API Gateway.
    - You can test any endpoint (logging in, checking nutrition, uploading images) directly from this page.

3.  **Check the Database:**
    - The database is running on port `5433` (as mapped in docker-compose).
    - You can connect via a tool like DBeaver or pgAdmin using:
        - **Host:** localhost
        - **Port:** 5433
        - **User:** user
        - **Password:** password
        - **Database:** mydatabase

---

## 5. Communication Patterns

- **External Communication:** HTTP/REST (User <-> API Gateway)
- **Internal Communication:** HTTP/REST (API Gateway <-> Microservices)
    - The services communicate over the internal Docker network.
    - For example, the Gateway calls `http://user-service:8000`. The hostname `user-service` is automatically resolved by Docker to the correct container IP.
