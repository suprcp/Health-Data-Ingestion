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

## Installation and Setup

### Database Setup
```sql
CREATE DATABASE health_data_db;
