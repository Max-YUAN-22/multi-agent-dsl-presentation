from core.base_agent import BaseAgent

class TrafficMonitorAgent(BaseAgent):
    def __init__(self, dsl_instance):
        super().__init__(
            dsl_instance=dsl_instance,
            role="Traffic Coordinator",
            capabilities=["monitor_traffic", "adjust_signal"]
        )

    def monitor_traffic(self, data):
        """
        Monitors traffic flow and adjusts signals during congestion.
        """
        print(f"Monitoring traffic at {data['location']} with speed {data['speed']} km/h")
        if data['speed'] < 20:  # Assuming speed < 20 km/h is congestion
            self.adjust_signal(data['location'])

    def adjust_signal(self, location):
        """
        Adjusts the traffic signal.
        """
        print(f"Adjusting traffic signal at {location} to handle congestion.")
