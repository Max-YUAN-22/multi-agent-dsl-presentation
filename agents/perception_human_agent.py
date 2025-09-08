from core.base_agent import BaseAgent

class PerceptionHumanAgent(BaseAgent):
    def __init__(self, dsl_instance):
        super().__init__(
            dsl_instance=dsl_instance,
            role="PerceptionHuman",
            capabilities=["fall"]
        )

    def fall(self, observation: str):
        """
        Detects a fall event.
        """
        print(f"PerceptionHumanAgent: Detecting fall: {observation}")
        return f"Fall detected: {observation}"