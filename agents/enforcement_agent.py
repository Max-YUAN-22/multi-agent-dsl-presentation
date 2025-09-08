from core.base_agent import BaseAgent

class EnforcementAgent(BaseAgent):
    def __init__(self, dsl_instance):
        super().__init__(
            dsl_instance=dsl_instance,
            role="Enforcement",
            capabilities=["law"]
        )

    def law(self, instruction: str):
        """
        Handles law enforcement tasks.
        """
        print(f"EnforcementAgent: Handling law enforcement task: {instruction}")
        return f"Law enforcement task '{instruction}' completed."