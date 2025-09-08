from core.base_agent import BaseAgent

class SprinklerAgent(BaseAgent):
    def __init__(self, dsl_instance):
        super().__init__(
            dsl_instance=dsl_instance,
            role="Sprinkler",
            capabilities=["irrigate"]
        )

    def irrigate(self, instruction: str):
        """
        Irrigates a zone.
        """
        print(f"SprinklerAgent: Irrigating with instruction: {instruction}")
        return f"Irrigation completed for: {instruction}"