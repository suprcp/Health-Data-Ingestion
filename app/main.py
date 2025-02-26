from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import threading
import logging

from .database import get_db, create_tables
from .models import HealthMetric
from .schemas import HealthMetricCreate, HealthMetricResponse
from .health_metric_tasks import HealthDataStream

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("health-api")

create_tables()

redis_processor = HealthDataStream()

stream_processing_active = False
stream_thread = None

app = FastAPI(app = FastAPI(
    title="Health Data API",
    description="Real-time health data processing service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
))

@app.get("/")
def read_root():
    return {"message": "Health Data API is running"}

def start_stream():
    global stream_processing_active, stream_thread

    if stream_processing_active:
        logger.info("Stream is already running")
        return

    stream_processing_active = True

    def run_processor():
        global stream_processing_active
        logger.info("Starting Redis Stream processor")
        try:
            redis_processor.process_stream()
        except Exception as e:
            logger.error(f"Stream processor error: {e}")
            stream_processing_active = False

    stream_thread = threading.Thread(target=run_processor, daemon=True)
    stream_thread.start()
    logger.info("Redis Stream processor thread started")


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application")
    start_stream()


@app.on_event("shutdown")
async def shutdown_event():
    global stream_processing_active
    logger.info("Shutting down the application")
    stream_processing_active = False


@app.post("/health-metrics/", status_code=201, response_model=HealthMetricResponse)
def save_health_data_json(
    metric: HealthMetricCreate,
    db: Session = Depends(get_db)
):
    new_metric = HealthMetric(
        user_id=metric.user_id,
        timestamp=datetime.utcnow(),
        heart_rate=metric.heart_rate,
        steps=metric.steps,
        calories=metric.calories
    )
    db.add(new_metric)
    db.commit()
    db.refresh(new_metric)
    return new_metric

@app.post("/health-metrics/params/", status_code=201, response_model=HealthMetricResponse)
def save_health_data_params(
    user_id: int = Query(...),
    heart_rate: int = Query(...),
    steps: int = Query(...),
    calories: float = Query(...),
    db: Session = Depends(get_db)
):
    new_metric = HealthMetric(
        user_id=user_id,
        timestamp=datetime.utcnow(),
        heart_rate=heart_rate,
        steps=steps,
        calories=calories
    )
    db.add(new_metric)
    db.commit()
    db.refresh(new_metric)
    return new_metric

@app.post("/health-metrics/stream/", status_code=202)
def queue_health_data(
        user_id: int = Query(...),
        heart_rate: int = Query(...),
        steps: int = Query(...),
        calories: float = Query(...),
):
    try:
        redis_processor.add_metric(user_id, heart_rate, steps, calories)
        return {"message": f"Metric for user {user_id} sent to processing queue"}
    except Exception as e:
        logger.error(f"Error sending metric to Redis Stream: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process metric: {str(e)}")


@app.get("/health-metrics/", response_model=List[HealthMetricResponse])
def read_health_metrics(db: Session = Depends(get_db)):
    metrics = db.query(HealthMetric).all()
    return metrics


@app.get("/health-metrics/{user_id}", response_model=List[HealthMetricResponse])
def read_user_metrics(user_id: int, db: Session = Depends(get_db)):
    metrics = db.query(HealthMetric).filter(HealthMetric.user_id == user_id).all()
    if not metrics:
        raise HTTPException(status_code=404, detail=f"No metrics found for user {user_id}")
    return metrics


class AggregatedMetricsResponse(BaseModel):
    user_id: Optional[int]
    start: Optional[datetime]
    end: Optional[datetime]
    average_heart_rate: float
    total_steps: int
    total_calories: float


@app.get("/metrics/aggregate", response_model=Dict[str, Any])
def get_aggregated_metrics(
        user_id: Optional[int] = Query(None, description="User ID to filter metrics"),
        start: Optional[datetime] = Query(None, description="Start time in ISO format"),
        end: Optional[datetime] = Query(None, description="End time in ISO format"),
        db: Session = Depends(get_db)
):
    query = db.query(
        func.avg(HealthMetric.heart_rate).label('average_heart_rate'),
        func.sum(HealthMetric.steps).label('total_steps'),
        func.sum(HealthMetric.calories).label('total_calories')
    )

    if user_id is not None:
        query = query.filter(HealthMetric.user_id == user_id)

    if start is not None:
        query = query.filter(HealthMetric.timestamp >= start)

    if end is not None:
        query = query.filter(HealthMetric.timestamp <= end)

    if user_id is not None:
        query = query.filter(HealthMetric.user_id == user_id)

    aggregated_metrics = query.one_or_none()

    if not aggregated_metrics or all(metric is None for metric in aggregated_metrics):
        raise HTTPException(status_code=404, detail="No metrics found for the given parameters")

    return {
        'user_id': user_id,
        'start': start,
        'end': end,
        'average_heart_rate': round(aggregated_metrics.average_heart_rate,
                                    2) if aggregated_metrics.average_heart_rate is not None else 0,
        'total_steps': int(aggregated_metrics.total_steps) if aggregated_metrics.total_steps is not None else 0,
        'total_calories': round(aggregated_metrics.total_calories,
                                2) if aggregated_metrics.total_calories is not None else 0
    }


@app.get("/stream/status")
def get_stream_status():
    try:
        status = {
            "stream_running": stream_processing_active,
            "messages_in_stream": redis_processor.redis_client.xlen(redis_processor.stream),
        }

        try:
            pending_info = redis_processor.redis_client.xpending(
                redis_processor.stream,
                redis_processor.group
            )
            status["pending_messages"] = pending_info.get("pending", 0)
        except Exception:
            status["pending_messages"] = "Couldn't fetch pending count"
        return status
    except Exception as e:
        logger.error(f"Couldn't get stream status: {e}")
        return {
            "stream_running": stream_processing_active,
            "error": str(e)
        }
