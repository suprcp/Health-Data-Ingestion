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
| Component      | Technology |
|---------------|------------|
| Backend       | FastAPI (Python) |
| Real-time processing | Redis Streams |
| Database      | PostgreSQL |
| ORM          | SQLAlchemy |
| Task processing | Multi-threading |

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
   CREATE DATABASE task_management_db;
   ```
# Install Redis and start the server
redis-server

# Clone the repository
git clone 

# Navigate to the project directory
cd Health-Data-Ingestion

# Create and activate a virtual environment
python -m venv venv_new
source venv_new/bin/activate 

# Install dependencies
pip install -r requirements.txt

# Copy the environment variables file
cp .env.example .env
# Modify .env based on your environment settings

# Start the application
uvicorn app.main:app --reload

