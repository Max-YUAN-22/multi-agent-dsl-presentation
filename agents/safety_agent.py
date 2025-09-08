from core.base_agent import BaseAgent

class SafetyAgent(BaseAgent):
    def __init__(self, dsl_instance):
        super().__init__(
            dsl_instance=dsl_instance,
            role="Safety Supervisor",
            capabilities=["monitor_safety", "trigger_alert"]
        )

    def monitor_safety(self, data):
        """
        Monitors the safety status of the city.
        """
        print(f"Monitoring safety at {data['location']} with status {data['safety_status']}")
        if data['safety_status'] == 'danger':
            self.trigger_alert(data['location'])

    def trigger_alert(self, location):
        """
        Triggers a safety alert.
        """
        print(f"Safety alert triggered at {location}.")

