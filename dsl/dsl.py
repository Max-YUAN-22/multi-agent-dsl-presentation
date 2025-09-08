
from __future__ import annotations
from typing import Any, Dict, Callable, List, Optional
import time

from runtime.radix_cache import RadixTrieCache
from runtime.scheduler import CacheAwareScheduler, Task
from runtime.eventbus import EventBus
from core.contracts import Contract
from utils.metrics import Metrics

ProgramFn = Callable[..., Any]

class TaskBuilder:
    """A builder for creating and configuring tasks before scheduling."""
    def __init__(self, dsl: DSL, name: str, prompt: str, agent: str):
        self._dsl = dsl
        self._task_params = {
            "name": name,
            "prompt": prompt,
            "agent": agent,
            "priority": 0,
            "timeout": 10.0,
            "max_retries": 0,
            "backoff_ms": 200,
            "constraint": None,
            "fallback_prompt": None,
        }

    def with_priority(self, priority: int) -> TaskBuilder:
        """Set the priority of the task."""
        self._task_params["priority"] = priority
        return self

    def with_timeout(self, timeout: float) -> TaskBuilder:
        """Set the timeout for the task in seconds."""
        self._task_params["timeout"] = timeout
        return self

    def with_retries(self, retries: int, backoff_ms: int = 200) -> TaskBuilder:
        """Configure retry logic for the task."""
        self._task_params["max_retries"] = retries
        self._task_params["backoff_ms"] = backoff_ms
        return self

    def with_contract(self, contract: Contract) -> TaskBuilder:
        """Attach a validation contract to the task."""
        self._task_params["constraint"] = contract
        return self

    def with_regex(self, regex: str) -> TaskBuilder:
        """Convenience method to add a regex-based contract."""
        contract_name = f"{self._task_params['name']}-re"
        self._task_params["constraint"] = Contract(name=contract_name, regex=regex)
        return self

    def with_fallback(self, fallback_prompt: str) -> TaskBuilder:
        """Provide a fallback prompt if the initial one fails."""
        self._task_params["fallback_prompt"] = fallback_prompt
        return self

    def schedule(self) -> Task:
        """Finalize and schedule the task for execution."""
        task = Task(**self._task_params)
        self._dsl.scheduler.add(task)
        return task

class DSL:
    """The main entrypoint for the DSL, providing methods to define and coordinate agentic tasks."""
    def __init__(self, seed: int = 7, workers:int=8):
        self.cache = RadixTrieCache()
        self.scheduler = CacheAwareScheduler(workers=workers)
        self.bus = EventBus()
        self._llm: Optional[Callable[[str, Optional[str]], str]] = None
        self.metrics = Metrics()

    def use_llm(self, llm_callable: Callable[[str, Optional[str]], str], *, use_cache: bool = True):
        """Configure the LLM callable for the DSL and scheduler."""
        self._llm = llm_callable
        self.scheduler.configure(llm=llm_callable, cache=self.cache, metrics=self.metrics, use_cache=use_cache)

    def gen(self, name: str, *, prompt: str, agent: str) -> TaskBuilder:
        """Generate a new task with a given name, prompt, and agent."""
        return TaskBuilder(self, name, prompt, agent)

    def join(self, tasks: List[Task], mode: str = "all", within_ms: Optional[int] = None) -> Dict[str, Any]:
        """Wait for tasks to complete based on the specified mode."""
        results: Dict[str, Any] = {}
        start = time.time()

        if mode == "all":
            for t in tasks:
                to = (within_ms / 1000.0) if within_ms else None
                results[t.name] = t.wait(timeout=to)
                if within_ms and (time.time() - start) >= (within_ms / 1000.0):
                    break
            return results
        elif mode == "any":
            while True:
                if within_ms and (time.time() - start) * 1000 > within_ms:
                    return results  # Timeout
                for t in tasks:
                    if t.is_done():
                        results[t.name] = t.wait(timeout=0)
                        return results
                time.sleep(0.01)  # Prevent busy-waiting
        else:
            raise ValueError(f"Unsupported join mode: {mode}")

    def on(self, topic: str, fn: Callable[[Any], None]):
        """Subscribe a function to a specific event topic."""
        self.bus.subscribe(topic, fn)

    def emit(self, topic: str, payload: Any):
        """Publish an event to a specific topic."""
        self.bus.publish(topic, payload)

    def run(self, llm_callable: Optional[Callable[[str, Optional[str]], str]] = None) -> Dict[str, Any]:
        """A placeholder run method, extendable for specific program execution logic."""
        if llm_callable:
            self.use_llm(llm_callable)
        elif self._llm is None:
            self.use_llm(lambda p, role=None: f"[mocked:{role}] {p}")
        return {}

def program(fn: ProgramFn) -> ProgramFn:
    """A decorator to mark a function as a DSL program."""
    fn.__is_dsl_program__ = True
    return fn
