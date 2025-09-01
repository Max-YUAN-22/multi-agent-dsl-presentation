
from __future__ import annotations
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass

@dataclass
class AgentDef:
    role: str
    capabilities: List[str]
    llm: Optional[Callable[[str, str], str]] = None

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, AgentDef] = {}
    def register(self, agent: AgentDef):
        self._agents[agent.role] = agent
    def get(self, role: str) -> AgentDef:
        return self._agents[role]
    def select(self, capability: str) -> str:
        for r, a in self._agents.items():
            if capability in a.capabilities:
                return r
        raise ValueError(f"No agent matches capability: {capability}")
