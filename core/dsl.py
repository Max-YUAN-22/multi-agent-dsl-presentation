
from __future__ import annotations
from typing import Any, Dict, Callable, List, Optional
import time

from runtime.radix_cache import RadixTrieCache
from runtime.scheduler import CacheAwareScheduler, Task
from runtime.eventbus import EventBus
from core.contracts import Contract
from core.agents import AgentRegistry, AgentDef
from utils.metrics import Metrics

ProgramFn = Callable[..., Any]

class DSL:
    def __init__(self, seed: int = 7, workers:int=8):
        self.cache = RadixTrieCache()
        self.scheduler = CacheAwareScheduler(workers=workers)
        self.bus = EventBus()
        self.agents = AgentRegistry()
        self._llm: Optional[Callable[[str, Optional[str]], str]] = None
        self.metrics = Metrics()

    def register(self, role: str, capabilities: List[str]):
        self.agents.register(AgentDef(role=role, capabilities=capabilities))

    def use_llm(self, llm_callable: Callable[[str, Optional[str]], str], *, use_cache: bool = True):
        self._llm = llm_callable
        self.scheduler.configure(llm=llm_callable, cache=self.cache, metrics=self.metrics, use_cache=use_cache)

    def gen(self, name: str, *, prompt: str, agent: str, regex: Optional[str]=None,
            contract: Optional[Contract]=None, priority:int=0, timeout:float=10.0,
            retries:int=0, backoff_ms:int=200, fallback: Optional[str]=None) -> Task:
        c = contract or (Contract(name=f"{name}-re", regex=regex) if regex else None)
        t = Task(name=name, prompt=prompt, agent=agent, priority=priority,
                 timeout=timeout, max_retries=retries, backoff_ms=backoff_ms,
                 constraint=c, fallback_prompt=fallback)
        self.scheduler.add(t)
        return t

    def delegate(self, parent: Task, name: str, *, prompt: str, agent: str, **kw) -> Task:
        return self.gen(name, prompt=prompt, agent=agent, **kw)

    def join(self, tasks: List[Task], mode: str = "all", within_ms: Optional[int]=None) -> Dict[str, Any]:
        results = {}
        start = time.time()
        for t in tasks:
            to = (within_ms/1000.0) if within_ms else None
            results[t.name] = t.wait(timeout=to)
            if within_ms and (time.time() - start) >= (within_ms/1000.0):
                break
        return results

    def on(self, topic: str, fn: Callable[[Any], None]):
        self.bus.subscribe(topic, fn)

    def emit(self, topic: str, payload: Any):
        self.bus.publish(topic, payload)

    def run(self, llm_callable: Optional[Callable[[str, Optional[str]], str]] = None) -> Dict[str, Any]:
        if llm_callable:
            self.use_llm(llm_callable)
        elif self._llm is None:
            self.use_llm(lambda p, role=None: f"[mocked:{role}] {p}")
        return {}

def program(fn: ProgramFn) -> ProgramFn:
    fn.__is_dsl_program__ = True
    return fn
