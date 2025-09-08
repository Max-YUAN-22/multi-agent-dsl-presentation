from core.base_agent import BaseAgent

class TrafficManagerAgent(BaseAgent):
    """An agent that controls traffic based on instructions."""
    def __init__(self, dsl_instance):
        super().__init__(
            dsl_instance=dsl_instance,
            role="TrafficManager",
            capabilities=["control"]
        )

    def control(self, instruction: str):
        """
        Controls traffic based on an instruction.
        """
        print(f"TrafficManagerAgent: Executing control instruction: {instruction}")
        return f"Control instruction '{instruction}' executed."