
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable, Tuple, List
import threading, time, queue

@dataclass
class Task:
    name: str
    prompt: str
    agent: Any
    priority: int = 0
    timeout: float = 10.0
    max_retries: int = 0
    backoff_ms: int = 200
    constraint: Any = None
    fallback_prompt: Optional[str] = None

    _result: Any = field(default=None, init=False)
    _event: threading.Event = field(default_factory=threading.Event, init=False)

    def set_result(self, val:Any):
        self._result = val
        self._event.set()

    def wait(self, timeout: Optional[float]=None) -> Any:
        self._event.wait(timeout)
        return self._result

class CacheAwareScheduler:
    """Priority = (longer prefix first, then higher task priority, then FIFO)."""
    def __init__(self, workers:int=8):
        self._q: "queue.PriorityQueue[Tuple[Tuple[int,int,int], Task]]" = queue.PriorityQueue()
        self._seq = 0
        self._stop = threading.Event()
        self._threads: List[threading.Thread] = []
        self._llm: Optional[Callable[[str, Optional[str]], str]] = None
        self._cache = None
        self._metrics = None
        self.use_cache = True
        for _ in range(max(1, workers)):
            th = threading.Thread(target=self._worker, daemon=True)
            th.start()
            self._threads.append(th)

    def configure(self, *, llm: Callable[[str, Optional[str]], str], cache, metrics=None, use_cache: bool = True):
        self._llm = llm
        self._cache = cache
        self._metrics = metrics
        self.use_cache = bool(use_cache)

    def add(self, t: Task):
        prefix_len = 0
        if self.use_cache and (self._cache is not None):
            try:
                prefix_len, _ = self._cache.get_with_lmp(t.prompt)
            except Exception:
                prefix_len = 0
        self._seq += 1
        key = (-int(prefix_len), -int(t.priority), self._seq)
        self._q.put((key, t))
        if self._metrics: self._metrics.on_submit()

    def _worker(self):
        while not self._stop.is_set():
            try:
                (key, t) = self._q.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                if t.name == "__stop__":
                    # 收到停机标记，退出该 worker
                    return
                self._execute_task(t)
            finally:
                self._q.task_done()


    def _execute_task(self, t: Task):
        cache_full_hit = False
        start_ts = time.time()
        if self.use_cache and (self._cache is not None):
            plen, hit_val = self._cache.get_with_lmp(t.prompt)
            if hit_val is not None and plen == len(t.prompt):
                cache_full_hit = True
                t.set_result(hit_val)
                if self._metrics:
                    self._metrics.on_complete((time.time()-start_ts)*1000.0, True)
                return
        out, ok = None, False
        attempts = 0
        agent_role = t.agent.role if hasattr(t.agent, 'role') else t.agent
        while attempts <= t.max_retries and not ok:
            try:
                out = self._llm(t.prompt, agent_role) if self._llm is not None else f"[LLM:{agent_role}] {t.prompt}"
                if t.constraint is not None:
                    if hasattr(t.constraint, 'validate'):
                        ok = bool(t.constraint.validate(out))
                    elif hasattr(t.constraint, 'valid'):
                        ok = bool(t.constraint.valid(out))
                    else:
                        ok = True
                else:
                    ok = True
            except Exception as e:
                out = f"[error:{t.name}] {e}"
                ok = False
            if not ok:
                attempts += 1
                if attempts <= t.max_retries:
                    time.sleep((t.backoff_ms/1000.0) * (2**(attempts-1)))
        if not ok and t.fallback_prompt:
            try:
                out = self._llm(t.fallback_prompt, agent_role) if self._llm else t.fallback_prompt
                ok = True
            except Exception as e:
                out = f"[error:{t.name}] {e}"
        if ok and self.use_cache and (self._cache is not None):
            try:
                self._cache.put(t.prompt, out)
            except Exception:
                pass
        t.set_result(out)
        if self._metrics:
            self._metrics.on_complete((time.time()-start_ts)*1000.0, cache_full_hit)

    def shutdown(self):
        # 推送与 worker 数量相同的停机任务，使用唯一自增序号避免 PriorityQueue 比较 Task
        for _ in self._threads:
            self._seq += 1
            stop_key = (-10**9, 0, self._seq)  # 极低优先级 + 递增序号
            self._q.put((stop_key, Task(name="__stop__", prompt="", agent="_")))
        # 等待线程收尾
        for th in self._threads:
            th.join(timeout=0.5)


    def run(self, cache, llm_callable: Callable[[str, Optional[str]], str], tasks: Optional[List[Task]]=None) -> Dict[str, Any]:
        self.configure(llm=llm_callable, cache=cache)
        pending: List[Task] = []
        if tasks:
            for t in tasks:
                pending.append(t)
                self.add(t)
        results: Dict[str, Any] = {}
        for t in pending:
            results[t.name] = t.wait(timeout=t.timeout + 60)
        return results
