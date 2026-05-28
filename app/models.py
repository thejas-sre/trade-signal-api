from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SignalRequest(BaseModel):
    symbol: str
    action: str
    confidence: float
    timestamp: datetime

class SignalResponse(BaseModel):
    signal_id: str
    symbol: str
    action: str
    confidence: float
    timestamp: datetime
    cached: bool

class HealthResponse(BaseModel):
    status: str
    redis_connected: bool
    version: str = "1.0.0"
