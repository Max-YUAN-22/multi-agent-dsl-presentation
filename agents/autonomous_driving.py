
from dsl.dsl import *
from agents.perception_agent import PerceptionAgent
from agents.traffic_manager_agent import TrafficManagerAgent
from agents.reroute_agent import RerouteAgent
from agents.ems_agent import EMSAgent
import random

class AutonomousDriving:
    def __init__(self, llm, seed=None, num_events=10):
        self.llm = llm
        self.seed = seed
        self.num_events = num_events
        self.perception_agent = PerceptionAgent(llm=self.llm)
        self.traffic_manager_agent = TrafficManagerAgent(llm=self.llm)
        self.reroute_agent = RerouteAgent(llm=self.llm)
        self.ems_agent = EMSAgent(llm=self.llm)
        self._setup_environment()

    def _setup_environment(self):
        if self.seed is not None:
            random.seed(self.seed)

    def _generate_event(self):
        # simplified event generation
        return {"event": "traffic incident"}

    def run_simulation(self):
        for i in range(self.num_events):
            event = self._generate_event()
            print(f"Cycle {i+1}/{self.num_events}: Processing event: {event}")
            self.process_event(event)

    def process_event(self, event):
        perception_task = Task(
            agent=self.perception_agent,
            instruction="Analyze the event and identify the type of incident."
        )
        traffic_manager_task = Task(
            agent=self.traffic_manager_agent,
            instruction="Based on the incident type, determine the necessary actions."
        )
        reroute_task = Task(
            agent=self.reroute_agent,
            instruction="Suggest a new route to avoid the incident."
        )
        ems_task = Task(
            agent=self.ems_agent,
            instruction="If necessary, dispatch emergency services."
        )

        # Define the workflow for event processing
        perception_task.set_downstream(traffic_manager_task)
        traffic_manager_task.set_downstream(reroute_task)
        traffic_manager_task.set_downstream(ems_task)

        # Start the workflow
        perception_task.run()

def driving_demo(llm, seed=None):
    simulation = AutonomousDriving(llm, seed)
    simulation.run_simulation()
