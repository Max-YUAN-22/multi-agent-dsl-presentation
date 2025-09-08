# backend/data_models.py
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class AutonomousDrivingEvent(BaseModel):
    timestamp: str
    road: str
    event_type: str
    severity: int
    vehicles: int
    lanes_blocked: int
    agent_latency_ms: float
    cache_hit: int
    clearance_time_s: float
    reroute_delay_s: float
    is_congested: int



class TrafficData(BaseModel):
    location: str = Field(min_length=1)
    traffic_volume: int = Field(ge=0, le=1000)

    @field_validator("location")
    @classmethod
    def non_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("location cannot be empty or all spaces")
        return v.strip()


class WeatherAlert(BaseModel):
    alert_type: str = Field(min_length=1)
    area: str = Field(min_length=1)


class ParkingData(BaseModel):
    location: str = Field(min_length=1)
    available_spots: int = Field(ge=0, le=10000)


class SafetyData(BaseModel):
    location: str = Field(min_length=1)
    safety_status: Literal["ok", "warning", "incident"]


class DispatchEventRequest(BaseModel):
    event: str
    location: str
    data: Optional[dict] = None


class GenerateReportRequest(BaseModel):
    location: Optional[str] = None
    weatherAlert: Optional[str] = None
    safetyStatus: Optional[Literal["ok", "warning", "incident"]] = None


class ReportRequest(BaseModel):
    location: Optional[str] = None
    event: Optional[str] = None
    safetyStatus: Optional[str] = None
    fireResponse: Optional[dict] = None
    weatherAlert: Optional[str] = None


class FireResponse(BaseModel):
    level: Literal["low", "medium", "high", "unknown"]
    units: int


class TrafficIncident(BaseModel):
    description: str
    location: str
    severity: int