from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class HealthMetricCreate(BaseModel):
    user_id: int
    heart_rate: int
    steps: int
    calories: float


class HealthMetricResponse(BaseModel):
    id: int
    user_id: int
    timestamp: datetime
    heart_rate: int
    steps: int
    calories: float

    class Config:
        from_attributes = True
