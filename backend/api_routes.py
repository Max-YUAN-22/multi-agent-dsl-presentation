# backend/api_routes.py
import asyncio
from fastapi import APIRouter, Depends
from backend.data_models import (
    AutonomousDrivingEvent,
    TrafficData,
    WeatherAlert,
    ParkingData,
    SafetyData,
    DispatchEventRequest,
    GenerateReportRequest,
    TrafficIncident,
)
from backend.dsl_workflows import (
    fire_alert_workflow_task,
    master_workflow_chain_task,
    run_simulation_workflow,
    traffic_incident_workflow_task,
)
from core.llm import generate_report_with_deepseek
from dsl.dsl import DSL

from agents.traffic_monitor_agent import TrafficMonitorAgent
from agents.weather_agent import WeatherAgent
from agents.parking_agent import ParkingAgent
from agents.safety_agent import SafetyAgent
from agents.traffic_incident_agent import TrafficIncidentAgent
from backend.dependencies import (
    get_dsl_instance,
    get_traffic_monitor_agent,
    get_weather_agent,
    get_parking_agent,
    get_safety_agent,
    get_traffic_incident_agent,
)
from backend.websocket_manager import manager

router = APIRouter()


@router.get("/health")
def health():
    return {"ok": True}


@router.post("/events/autonomous_driving")
async def autonomous_driving(evt: AutonomousDrivingEvent):
    payload = evt.dict()
    message = {
        "type": "autonomous_driving",
        "payload": payload,
        "title": "Autonomous Driving Event",
    }
    print(f"Broadcasting event: {message}")
    await manager.broadcast(message)
    return {"status": "received"}


@router.post("/events/traffic_monitor")
async def traffic_monitor(
    data: TrafficData, traffic_monitor_agent: TrafficMonitorAgent = Depends(get_traffic_monitor_agent)
):
    traffic_monitor_agent.monitor_traffic(data.dict())
    message = {
        "type": "traffic_monitor",
        "payload": data.dict(),
        "title": "Traffic Monitor",
    }
    print(f"Broadcasting event: {message}")
    await manager.broadcast(message)
    return {"status": "success"}


@router.post("/events/weather_alert")
async def weather_alert(alert: WeatherAlert, weather_agent: WeatherAgent = Depends(get_weather_agent), dsl: DSL = Depends(get_dsl_instance)):
    weather_agent.trigger_weather_alert(alert.dict())
    message = {
        "type": "weather_alert",
        "payload": alert.dict(),
        "title": "Weather Alert",
    }
    print(f"Broadcasting event: {message}")
    await manager.broadcast(message)
    asyncio.create_task(master_workflow_chain_task(dsl, alert.dict()))
    return {"status": "alert triggered"}


@router.post("/events/parking_update")
async def parking_update(data: ParkingData, parking_agent: ParkingAgent = Depends(get_parking_agent)):
    parking_agent.update_parking_status(data.dict())
    message = {
        "type": "parking_update",
        "payload": data.dict(),
        "title": "Parking Update",
    }
    print(f"Broadcasting event: {message}")
    await manager.broadcast(message)
    return {"status": "updated"}


@router.post("/events/safety_monitor")
async def safety_monitor(data: SafetyData, safety_agent: SafetyAgent = Depends(get_safety_agent)):
    safety_agent.monitor_safety(data.dict())
    message = {
        "type": "safety_monitor",
        "payload": data.dict(),
        "title": "Safety Monitor",
    }
    print(f"Broadcasting event: {message}")
    await manager.broadcast(message)
    return {"status": "monitoring"}


@router.post("/run_simulation/{simulation_name}")
async def run_simulation(simulation_name: str, dsl: DSL = Depends(get_dsl_instance)):
    asyncio.create_task(run_simulation_workflow(dsl, simulation_name))
    return {"status": f"simulation '{simulation_name}' started"}


@router.post("/dispatch-event")
async def dispatch_event(req: DispatchEventRequest, dsl: DSL = Depends(get_dsl_instance)):
    if req.event == "fire_alert":
        event_data = {"location": req.location, "details": "Dispatch event"}
        asyncio.create_task(fire_alert_workflow_task(dsl, event_data))
        return {"status": "fire_alert workflow started"}
    return {"status": "event received, but no handler defined", "event": req.event}


@router.post("/generate-report")
async def generate_report(req: GenerateReportRequest):
    report_text = await generate_report_with_deepseek(
        {
            "location": req.location,
            "weatherAlert": req.weatherAlert,
            "safetyStatus": req.safetyStatus,
        }
    )
    return {"report": report_text}


@router.post("/events/traffic_incident")
async def traffic_incident(
    incident: TrafficIncident, traffic_incident_agent: TrafficIncidentAgent = Depends(get_traffic_incident_agent), dsl: DSL = Depends(get_dsl_instance)
):
    traffic_incident_agent.process(incident.dict())
    message = {
        "type": "traffic_incident",
        "payload": incident.dict(),
        "title": "Traffic Incident",
    }
    print(f"Broadcasting event: {message}")
    await manager.broadcast(message)
    asyncio.create_task(traffic_incident_workflow_task(dsl, incident.dict()))
    return {"status": "incident reported"}