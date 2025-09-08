from core.base_agent import BaseAgent

class PerceptionEnvAgent(BaseAgent):
    def __init__(self, dsl_instance):
        super().__init__(
            dsl_instance=dsl_instance,
            role="PerceptionEnv",
            capabilities=["env"]
        )

    def env(self, observation: str):
        """
        Senses environmental data.
        """
        print(f"PerceptionEnvAgent: Sensing environment: {observation}")
        return f"Environment sensed: {observation}"