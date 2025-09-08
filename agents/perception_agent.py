from core.base_agent import BaseAgent

class PerceptionAgent(BaseAgent):
    """An agent responsible for detecting incidents from scene descriptions."""
    def __init__(self, dsl_instance):
        super().__init__(
            dsl_instance=dsl_instance,
            role="Perception",
            capabilities=["detect_incident"]
        )

    def detect_incident(self, scene: str):
        """
        Detects an incident from a scene description.
        """
        print(f"PerceptionAgent: Detecting incident in scene: {scene}")
        # In a real scenario, this would involve more complex logic
        return f"Incident detected: {scene}"