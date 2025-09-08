from __future__ import annotations
from dsl.dsl import *
from analysis.api_clients import OverpassClient, OpenMeteoClient
from agents.perception_agent import PerceptionAgent
from agents.traffic_manager_agent import TrafficManagerAgent
from agents.reroute_agent import RerouteAgent
from agents.ems_agent import EMSAgent
import random

# BBox for a small area in San Francisco (S, W, N, E)
BBOX = (37.76, -122.46, 37.80, -122.39)
SF_LAT, SF_LON = 37.7749, -122.4194

class ADRealtime:
    def __init__(self, llm, seed=None):
        self.llm = llm
        self.seed = seed
        self.perception_agent = PerceptionAgent(llm=self.llm)
        self.traffic_manager_agent = TrafficManagerAgent(llm=self.llm)
        self.reroute_agent = RerouteAgent(llm=self.llm)
        self.ems_agent = EMSAgent(llm=self.llm)
        self._setup_environment()

    def _setup_environment(self):
        if self.seed is not None:
            random.seed(self.seed)

    def _fetch_road_network(self):
        op = OverpassClient()
        bbox_str = f"{BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]}"
        roads = op.fetch_roads(bbox_str)
        return [el["id"] for el in roads.get("elements", []) if el.get("type") == "way"]

    def _fetch_weather_conditions(self):
        om = OpenMeteoClient()
        wx = om.fetch_weather(SF_LAT, SF_LON)
        try:
            return float(wx["hourly"]["precipitation"][-1])
        except Exception:
            return 0.0

    def run_simulation(self, ticks=120):
        way_ids = self._fetch_road_network()
        if not way_ids:
            print("No road network data available.")
            return

        rain = self._fetch_weather_conditions()
        base_p = 0.01
        p_collision = base_p + min(rain * 0.02, 0.2)  # Cap at 0.21

        for i in range(ticks):
            if random.random() < p_collision:
                wid = random.choice(way_ids)
                print(f"Cycle {i+1}/{ticks}: Processing incident on way: {wid}")
                self.process_incident(wid)

    def process_incident(self, way_id):
        scene = f"Incident near way:{way_id}. Vehicles stopped."
        perception_task = Task(
            agent=self.perception_agent,
            instruction=f"Analyze the incident: {scene}"
        )
        traffic_manager_task = Task(
            agent=self.traffic_manager_agent,
            instruction=f"Close way:{way_id} temporarily."
        )
        reroute_task = Task(
            agent=self.reroute_agent,
            instruction=f"Reroute around way:{way_id}."
        )
        ems_task = Task(
            agent=self.ems_agent,
            instruction=f"Dispatch tow to way:{way_id}."
        )

        perception_task.set_downstream(traffic_manager_task)
        traffic_manager_task.set_downstream(reroute_task)
        traffic_manager_task.set_downstream(ems_task)

        perception_task.run()

def ad_realtime(llm, seed=None):
    simulation = ADRealtime(llm, seed)
    simulation.run_simulation()
