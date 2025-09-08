from core.base_agent import BaseAgent

class SanitationAgent(BaseAgent):
    def __init__(self, dsl_instance):
        super().__init__(
            dsl_instance=dsl_instance,
            role="Sanitation",
            capabilities=["cleaning"]
        )

    def cleaning(self, instruction: str):
        """
        Handles cleaning tasks.
        """
        print(f"SanitationAgent: Handling cleaning task: {instruction}")
        return f"Cleaning task '{instruction}' completed."