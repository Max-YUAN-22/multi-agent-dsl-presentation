
from __future__ import annotations
from typing import Any, Callable, Dict, List
import threading, queue

class EventBus:
    """Single background worker + bounded queue to avoid thread explosions."""
    def __init__(self, max_queue:int=8192):
        self._subs: Dict[str, List[Callable[[Any], None]]] = {}
        self._lock = threading.RLock()
        self._q: "queue.Queue[tuple[str, Any]]" = queue.Queue(maxsize=max_queue)
        self._stop = threading.Event()
        self._th = threading.Thread(target=self._loop, daemon=True)
        self._th.start()

    def _loop(self):
        while not self._stop.is_set():
            try:
                topic, payload = self._q.get(timeout=0.1)
            except queue.Empty:
                continue
            with self._lock:
                fns = list(self._subs.get(topic, []))
            for fn in fns:
                try:
                    fn(payload)
                except Exception:
                    pass
            self._q.task_done()

    def subscribe(self, topic: str, fn: Callable[[Any], None]):
        with self._lock:
            self._subs.setdefault(topic, []).append(fn)

    def publish(self, topic: str, payload: Any):
        try:
            self._q.put_nowait((topic, payload))
        except queue.Full:
            pass  # drop for MVP

    def shutdown(self):
        self._stop.set()
        self._th.join(timeout=0.5)
