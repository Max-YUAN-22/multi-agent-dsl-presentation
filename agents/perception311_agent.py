from core.base_agent import BaseAgent

class Perception311Agent(BaseAgent):
    def __init__(self, dsl_instance):
        super().__init__(
            dsl_instance=dsl_instance,
            role="Perception311",
            capabilities=["city_event"]
        )

    def city_event(self, observation: str):
        """
        Processes a 311 city event.
        """
        print(f"Perception311Agent: Processing city event: {observation}")
        return f"City event '{observation}' processed."