# core/base_agent.py
from __future__ import annotations
from typing import List, Optional, Callable, Any

class BaseAgent:
    """Base class for all agents, providing a standard interface for integration with the DSL."""

    def __init__(self, dsl_instance: 'DSL', role: str, capabilities: List[str]):
        self._dsl = dsl_instance
        self._role = role
        self._capabilities = capabilities

    @property
    def role(self) -> str:
        """The role of the agent."""
        return self._role

    @property
    def capabilities(self) -> List[str]:
        """The capabilities of the agent."""
        return self._capabilities

    def gen(self, name: str, *, prompt: str, **kwargs) -> 'Task':
        """A convenience method to generate a task for this agent."""
        return self._dsl.gen(name, prompt=prompt, agent=self.role, **kwargs)

    def on(self, topic: str, fn: Callable[[Any], None]):
        """Subscribes to a topic on the event bus."""
        self._dsl.on(topic, fn)

    def emit(self, topic: str, payload: Any):
        """Emits an event to the event bus."""
        self._dsl.emit(topic, payload)