from core.base_agent import BaseAgent

class EMSAgent(BaseAgent):
    """An agent that dispatches Emergency Medical Services (EMS) based on instructions."""
    def __init__(self, dsl_instance):
        super().__init__(
            dsl_instance=dsl_instance,
            role="EMS",
            capabilities=["dispatch"]
        )

    def dispatch(self, instruction: str):
        """
        Dispatches EMS based on an instruction.
        """
        print(f"EMSAgent: Dispatching for: {instruction}")
        return f"EMS dispatched for '{instruction}'."