💪 AI Fitness & Diet Recommendation System
A full-stack, containerized web application built with FastAPI and Streamlit that provides personalized fitness metrics, BMI analysis, and daily calorie/macro-nutrient requirements based on user goals.

🚀 Features
Structured API: Backend built with FastAPI using Pydantic for strict data validation.

Interactive UI: Frontend built with Streamlit featuring easy-to-use tabs for profile creation and updates.

Professional Payloads: Nested JSON responses grouped into account, profile, and metrics.

Data Persistence: Uses a local JSON database mapped via Docker Volumes so your data survives container restarts.

Containerized: Fully orchestrated using Docker Compose for seamless deployment.

🛠️ Tech Stack
Backend: FastAPI, Pydantic, Uvicorn

Frontend: Streamlit, Requests

DevOps: Docker, Docker Compose

Data: JSON (Persistent File Storage)

📦 Installation & Setup
Prerequisites
Docker Desktop installed and running.

Quick Start
Clone the repository:

Bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
Run with Docker Compose:

Bash
docker-compose up --build
Access the Application:

Frontend UI: http://localhost:8501

Interactive API Docs (Swagger): http://localhost:8000/docs

📊 API Structure
The API follows a structured nested response format:

JSON
{
  "account": { "user_id": "...", "created_at": "...", "updated_at": "..." },
  "profile": { "name": "...", "email": "...", "age": "...", "goal": "..." },
  "metrics": { "bmi": "...", "recommended_calories": "...", "macros": "..." }
}
🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.