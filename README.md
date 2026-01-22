# Ecommerce Store Full Stack based on Streamlit

This project is a full-stack ecommerce application built using Streamlit (Frontend) and FastAPI (Backend).

## Structure

- `app.py`: Main Streamlit entry point.
- `backend/`: FastAPI backend application.
- `config/`: Configuration settings and database connection.
- `data/`: Raw and processed data.
- `models/`: Machine learning models for recommendation and analytics.
- `services/`: Business logic services.
- `ui/`: Streamlit UI pages.
- `utils/`: Helper functions.
- `database/`: SQLite database.
- `docker/`: Docker configuration.

## How to Run

### 1. Run Streamlit Frontend (Standalone)
This runs the UI which directly interacts with the services/database.

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

### 2. Run FastAPI Backend (Optional)
To run the API server for external access or mobile apps:

```bash
uvicorn backend.main:app --reload
```
API Documentation will be available at: http://127.0.0.1:8000/docs

### 3. Run with Docker
To run both services using Docker Compose:

```bash
docker-compose -f docker/docker-compose.yml up --build
```
- Frontend: http://localhost:8501
- Backend: http://localhost:8000
