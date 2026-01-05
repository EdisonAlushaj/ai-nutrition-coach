# AI Nutrition Coach & Meal Planner

An intelligent, distributed backend system that leverages AI for food recognition and provides personalized nutritional coaching.

## 🏗️ Architecture
*   **Microservices Paradigm:** Architected as five independent, containerized services for high scalability and clear separation of concerns.
*   **Factory Design Pattern:** Used to dynamically select meal-planning strategies based on user goals (e.g., muscle gain vs. weight loss).
*   **API Gateway:** A central entry point to manage traffic and route requests to downstream services.

## 🛠️ Tech Stack
*   **Language:** Python 3.x
*   **Framework:** FastAPI (Asynchronous REST APIs)
*   **AI/ML:** TensorFlow & Keras (MobileNetV2 for Image Recognition)
*   **DevOps:** Docker & Docker Compose
*   **Database:** PostgreSQL with SQLAlchemy ORM
*   **Security:** JSON Web Tokens (JWT) for inter-service communication

## 🚀 Key Features
*   **Computer Vision Food Logging:** Upload an image of food; the AI identifies the items and logs nutritional data automatically.
*   **Automated Analytics:** Real-time summary of daily intake versus personalized targets.
*   **Asynchronous Processing:** High-performance API handling for a seamless user experience.
*   **Containerized Workflow:** Fully orchestrated with Docker for easy deployment and environment consistency.

## 🚦 Getting Started
1. Clone the repo: `git clone https://github.com/EdisonAlushaj/ai-nutrition-coach`
2. Ensure Docker Desktop is installed.
3. Run `docker-compose up --build`.
4. Access the API documentation at `http://localhost:8000/docs`.
