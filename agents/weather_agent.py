# agents/weather_agent.py
from core.base_agent import BaseAgent

class WeatherAgent(BaseAgent):
    def __init__(self, dsl_instance):
        super().__init__(dsl_instance, 'weather', ['trigger_weather_alert', 'activate_drainage_system'])

    def trigger_weather_alert(self, alert):
        """
        Triggers actions based on a weather alert.
        """
        print(f"Weather alert triggered: {alert['alert_type']} in {alert['area']}")
        if alert['alert_type'] == 'rain':
            self.activate_drainage_system(alert['area'])

    def activate_drainage_system(self, area):
        """
        Activates the drainage system.
        """
        print(f"Activating drainage system in {area}.")
