
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
import threading, time, csv, os

@dataclass
class MetricsEvent:
    t_end: float
    latency_ms: float
    cache_hit: bool

class Metrics:
    """Thread-safe metrics recorder for Scheduler. CSV-friendly export."""
    def __init__(self):
        self._lock = threading.RLock()
        self.events: List[MetricsEvent] = []
        self.task_started = 0
        self.task_completed = 0
        self.cache_hits_full = 0

    def on_submit(self):
        with self._lock:
            self.task_started += 1

    def on_complete(self, latency_ms: float, cache_hit: bool):
        with self._lock:
            self.task_completed += 1
            if cache_hit:
                self.cache_hits_full += 1
            self.events.append(MetricsEvent(time.time(), latency_ms, cache_hit))

    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            total = self.task_completed
            hit_rate = (self.cache_hits_full / total) if total else 0.0
            avg_latency = (sum(e.latency_ms for e in self.events) / total) if total else 0.0
            return {
                "task_started": self.task_started,
                "task_completed": total,
                "cache_hit_rate": hit_rate,
                "avg_latency_ms": avg_latency,
            }

    def write_csv(self, outdir: str):
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, "events.csv")
        with self._lock, open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["t_end", "latency_ms", "cache_hit"])
            for e in self.events:
                w.writerow([f"{e.t_end:.6f}", f"{e.latency_ms:.3f}", int(e.cache_hit)])
        s = self.to_dict()
        path2 = os.path.join(outdir, "summary.csv")
        with open(path2, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(list(s.keys()))
            w.writerow(list(s.values()))
