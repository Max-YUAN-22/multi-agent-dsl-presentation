import asyncio
from typing import Dict, Any
from backend.dependencies import get_dsl_instance, get_websocket_manager
from dsl.dsl import DSL

async def broadcast_message_task(dsl: DSL, message: str):
    """Broadcasts a message to all connected WebSocket clients."""
    await get_websocket_manager().broadcast(message)

async def fire_alert_workflow_task(dsl: DSL, event_data: dict):
    """Workflow for handling fire alerts."""
    dsl.gen(
        name="broadcast_fire_alert",
        prompt=f"Broadcasting fire alert: {event_data}",
        agent="broadcast_agent"
    ).schedule()
    
    safety_check_task = dsl.gen(
        name="safety_protocol_check",
        prompt="Confirm all safety protocols are active for a fire emergency.",
        agent="safety_agent"
    ).schedule()

    report_task = dsl.gen(
        name="generate_fire_report",
        prompt=f"Generate a detailed report for the fire event: {event_data}",
        agent="reporting_agent"
    ).schedule()

    await broadcast_message_task(dsl, {
        "type": "fire_alert",
        "title": "Fire Alert",
        "payload": event_data
    })
    
    await asyncio.to_thread(dsl.join, [safety_check_task, report_task], mode="all")

async def traffic_incident_workflow_task(dsl: DSL, event_data: dict):
    """Workflow for handling traffic incidents."""
    dsl.gen(
        name="broadcast_traffic_incident",
        prompt=f"Broadcasting traffic incident: {event_data}",
        agent="broadcast_agent"
    ).schedule()

    reroute_task = dsl.gen(
        name="calculate_optimal_reroute",
        prompt=f"Calculate optimal rerouting for traffic incident at {event_data['location']}",
        agent="traffic_agent"
    ).schedule()

    await broadcast_message_task(dsl, {
        "type": "traffic_incident",
        "title": "Traffic Incident",
        "payload": event_data
    })
    
    await asyncio.to_thread(dsl.join, [reroute_task])

async def master_workflow_chain_task(dsl: DSL, event_data: dict):
    """Workflow for handling weather alerts, which may trigger other workflows."""
    dsl.gen(
        name="broadcast_weather_alert",
        prompt=f"Broadcasting weather alert: {event_data}",
        agent="broadcast_agent"
    ).schedule()

    await broadcast_message_task(dsl, {
        "type": "weather_alert",
        "title": "Weather Alert",
        "payload": event_data
    })
    
    if "fire" in event_data.get("secondary_risks", []):
        fire_event = {
            "location": event_data["area"],
            "details": "Secondary fire risk due to weather conditions."
        }
        await fire_alert_workflow_task(dsl, fire_event)


async def run_simulation_workflow(dsl: DSL, simulation_name: str):
    """Runs a specified simulation and broadcasts its events."""
    if simulation_name == "smart_city":
        from agents.smart_city import SmartCity
        city = SmartCity(dsl, llm_delay_ms=0, use_cache=True)
        
        # Subscribe to all events and broadcast them
        def event_handler(event):
            asyncio.create_task(get_websocket_manager().broadcast({
                "type": "simulation_event",
                "payload": event,
                "title": "Smart City Simulation"
            }))
        
        # Subscribe to DSL's event bus
        dsl.on("*", event_handler)
        
        # Run simulation with default parameters
        city_demo_task = dsl.gen(
            name="city_demo",
            prompt="Running smart city simulation",
            agent="simulation_agent"
        ).schedule()
        
        await asyncio.to_thread(dsl.join, [city_demo_task])
    else:
        await broadcast_message_task(dsl, {
            "type": "error",
            "title": "Unknown Simulation",
            "payload": {"simulation_name": simulation_name}
        })


@dsl.task
def autonomous_driving_workflow_task(event: dict):
    """
    A workflow task for autonomous driving.
    """
    print(
        f"Executing autonomous driving workflow for event: {event}"
    )
    # Simulate autonomous driving logic
    time.sleep(2)
    broadcast_message_task.run(
        {
            "type": "autonomous_driving",
            "title": "Autonomous Driving Task Updated",
            "payload": event,
        }
    )


@dsl.task
def parking_update_workflow_task(event: dict):
    """
    A workflow task for parking updates.
    """
    print(f"Executing parking update workflow for event: {event}")
    # Simulate parking update logic
    time.sleep(1)
    broadcast_message_task.run(
        {
            "type": "parking_update",
            "title": "Parking Update",
            "payload": event,
        }
    )


@dsl.task
def safety_inspection_workflow_task(event: dict):
    """
    A workflow task for safety inspections.
    """
    print(f"Executing safety inspection workflow for event: {event}")
    # Simulate safety inspection logic
    time.sleep(3)
    broadcast_message_task.run(
        {
            "type": "safety_inspection",
            "title": "Safety Inspection Update",
            "payload": event,
        }
    )


@dsl.task
def weather_alert_workflow_task(event: dict):
    """
    A workflow task for weather alerts.
    """
    print(f"Executing weather alert workflow for event: {event}")
    # Simulate weather alert logic
    time.sleep(1)
    broadcast_message_task.run(
        {
            "type": "weather_alert",
            "title": "Weather Alert",
            "payload": event,
        }
    )


@dsl.task
def run_simulation_workflow(task_name: str, event: dict):
    """Runs a specified simulation and broadcasts its events."""
    if simulation_name == "smart_city":
        from agents.smart_city import SmartCity
        city = SmartCity(dsl, llm_delay_ms=0, use_cache=True)
        
        # Subscribe to all events and broadcast them
        def event_handler(event):
            asyncio.create_task(get_websocket_manager().broadcast({
                "type": "simulation_event",
                "payload": event,
                "title": "Smart City Simulation"
            }))
        
        # Subscribe to DSL's event bus
        dsl.on("*", event_handler)
        
        # Run simulation with default parameters
        city_demo_task = dsl.gen(
            name="city_demo",
            prompt="Running smart city simulation",
            agent="simulation_agent"
        ).schedule()
        
        await asyncio.to_thread(dsl.join, [city_demo_task])
    else:
        await broadcast_message_task(dsl, {
            "type": "error",
            "title": "Unknown Simulation",
            "payload": {"simulation_name": simulation_name}
        })