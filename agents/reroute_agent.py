from core.base_agent import BaseAgent

class RerouteAgent(BaseAgent):
    """An agent responsible for planning reroutes based on instructions."""
    def __init__(self, dsl_instance):
        super().__init__(
            dsl_instance=dsl_instance,
            role="Reroute",
            capabilities=["plan"]
        )

    def plan(self, instruction: str):
        """
        Plans a reroute based on an instruction.
        """
        print(f"RerouteAgent: Planning reroute for: {instruction}")
        return f"Reroute planned for '{instruction}'."