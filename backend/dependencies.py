from core.llm import get_llm
from dsl.dsl import DSL
from agents.traffic_manager_agent import TrafficManagerAgent
from agents.traffic_monitor_agent import TrafficMonitorAgent
from agents.traffic_incident_agent import TrafficIncidentAgent
from agents.reroute_agent import RerouteAgent
from agents.perception_agent import PerceptionAgent
from agents.perception_human_agent import PerceptionHumanAgent
from agents.perception_env_agent import PerceptionEnvAgent
from agents.enforcement_agent import EnforcementAgent
from agents.ems_agent import EMSAgent
from agents.weather_agent import WeatherAgent
from agents.sanitation_agent import SanitationAgent
from agents.parking_agent import ParkingAgent
from agents.safety_agent import SafetyAgent
from backend.websocket_manager import manager as websocket_manager

llm = get_llm()
dsl_instance = DSL(workers=8)
dsl_instance.use_llm(llm)

traffic_manager_agent = TrafficManagerAgent(dsl_instance=dsl_instance)
traffic_monitor_agent = TrafficMonitorAgent(dsl_instance=dsl_instance)
traffic_incident_agent = TrafficIncidentAgent(dsl_instance=dsl_instance)
reroute_agent = RerouteAgent(dsl_instance=dsl_instance)
perception_agent = PerceptionAgent(dsl_instance=dsl_instance)
perception_human_agent = PerceptionHumanAgent(dsl_instance=dsl_instance)
perception_env_agent = PerceptionEnvAgent(dsl_instance=dsl_instance)
enforcement_agent = EnforcementAgent(dsl_instance=dsl_instance)
ems_agent = EMSAgent(dsl_instance=dsl_instance)
weather_agent = WeatherAgent(dsl_instance=dsl_instance)
sanitation_agent = SanitationAgent(dsl_instance=dsl_instance)
parking_agent = ParkingAgent(dsl_instance=dsl_instance)
safety_agent = SafetyAgent(dsl_instance=dsl_instance)

def get_dsl_instance():
    return dsl_instance

def get_traffic_manager_agent():
    return traffic_manager_agent

def get_traffic_monitor_agent():
    return traffic_monitor_agent

def get_traffic_incident_agent():
    return traffic_incident_agent

def get_reroute_agent():
    return reroute_agent

def get_perception_agent():
    return perception_agent

def get_perception_human_agent():
    return perception_human_agent

def get_perception_env_agent():
    return perception_env_agent

def get_enforcement_agent():
    return enforcement_agent

def get_ems_agent():
    return ems_agent

def get_weather_agent():
    return weather_agent

def get_sanitation_agent():
    return sanitation_agent

def get_parking_agent():
    return parking_agent

def get_safety_agent():
    return safety_agent

def get_websocket_manager():
    return websocket_manager