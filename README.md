# Health-Data-Ingestion

## Introduction
Health-Data-Ingestion is a real-time health data processing service that collects and analyzes simulated wearable health metrics (such as heart rate, steps, and calories burned). This system uses Redis Streams for real-time ingestion, PostgreSQL for data storage, and FastAPI for API interactions.

With high scalability and real-time processing, this project is designed for handling large-scale health data analytics.

---

## Features
- Real-time data ingestion via Redis Streams
- Persistent storage using PostgreSQL
- Aggregated data query API with time and user filtering
- Real-time stream processing using a multi-threaded worker
- FastAPI-based RESTful API

---

## Tech Stack
- Backend: FastAPI (Python)
- Real-time processing: Redis Streams
- Database: PostgreSQL
- ORM: SQLAlchemy
- Task processing: Multi-threading

---

## Prerequisites
- Python 3.9+
- PostgreSQL
- Redis
- `pip` for dependency management

---

### Database Setup
1. Install PostgreSQL following the [official documentation](https://www.postgresql.org/download/).
2. Create a new database:
   ```
   psql -U postgres template1;
   CREATE DATABASE health_data_db;
   ```
   
### Backend Setup 
1. Install Redis and Start the Server
    ```
    brew install redis
    redis-server
    ```
    
2. Clone the repository
   ```
   git clone https://github.com/suprcp/Health-Data-Ingestion.git
   ```

3. Navigate to the project directory
   ```
   cd Health-Data-Ingestion
   ```

4. Create and activate a virtual environment
   ```
   python -m venv venv_new
   source venv_new/bin/activate 
   ```
5. Install dependencies
   ```
   pip install -r requirements.txt
   ```

6. Modify .env based on your environment settings

7. Start the application
   ```
   uvicorn app.main:app --reload
   ```

The application will be available at: http://localhost:8000

### API Endpoints

- `POST /health-metrics/` – Add health data directly
- `POST /health-metrics/stream/` – Stream health data via Redis
- `GET /health-metrics/` – Get all health data
- `GET /health-metrics/{user_id}` – Get health data for a specific user
- `GET /metrics/aggregate` – GET /metrics/aggregate
- `Check Redis Stream status` – GET /stream/status

### Testing
- Swagger UI
- You can test all API endpoints via Swagger UI:http://localhost:8000/docs













