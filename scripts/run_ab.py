# -*- coding: utf-8 -*-
"""
A/B runner: NoCache vs WithCache
- 针对 scenario {city, ad}，各跑一遍，统一采集 events.csv / summary.csv
- 无需修改 agents：用 monkeypatch 包裹 scheduler 执行，记录每个 Task 的延迟与缓存命中
- 默认写入:
    results/<scenario>_no_cache/{events.csv, summary.csv}
    results/<scenario>_with_cache/{events.csv, summary.csv}
用法:
    PYTHONPATH=. python scripts/run_ab.py --scenario city --ticks 300 --seed 7
    PYTHONPATH=. python scripts/run_ab.py --scenario ad   --ticks 300 --seed 7
"""

import os, sys, csv, time, argparse, math, json
from datetime import datetime, timezone
from typing import Tuple

from dsl.dsl import DSL
from runtime.radix_cache import RadixTrieCache

# 你的程序入口函数（agents 是“程序”，需要传 DSL 进去）
from agents.smart_city import city_demo as _city_program
from agents.autonomous_driving import driving_demo as _ad_program

# 如已集成星火适配器，会优先用真实 LLM；若没配置凭据，会 fallback 到 mock
try:
    from integrations.spark_x1 import get_llm_with_fallback
except Exception:
    get_llm_with_fallback = lambda : (lambda p, role=None: f"[mock:{role}] {p}")


class _DummyNoopCache:
    """用于 NoCache：永远 miss；put 不生效。"""
    def get_with_lmp(self, key:str):
        return 0, None
    def put(self, key, value):
        pass


def _ensure_dir(d):
    os.makedirs(d, exist_ok=True)


def _run_one(scenario:str, ticks:int, seed:int, outdir:str, use_cache:bool=True) -> dict:
    """
    运行一次场景，采集 events.csv 与 summary.csv，并返回汇总。
    """
    _ensure_dir(outdir)
    events_path = os.path.join(outdir, "events.csv")
    summary_path = os.path.join(outdir, "summary.csv")

    # ---------- 准备 DSL ----------
    dsl = DSL(workers=16)  # 可按你配额调大
    # 缓存开关：替换 dsl.cache
    dsl.cache = RadixTrieCache() if use_cache else _DummyNoopCache()

    real_use_llm = dsl.use_llm
    def _locked_use_llm(*args, **kwargs):
        return  # 忽略一切覆盖请求（含 use_cache 等）
    dsl.use_llm = _locked_use_llm  # type: ignore
    llm = get_llm_with_fallback()
    real_use_llm(llm)  # 设置一次



    # ---------- 指标打点：猴补丁 scheduler._execute_task ----------
    scheduler = dsl.scheduler
    orig_exec = scheduler._execute_task

    # 事件写入器
    f_ev = open(events_path, "w", newline="", encoding="utf-8")
    ev = csv.DictWriter(f_ev, fieldnames=[
        "timestamp","scenario","agent","name","prompt_len",
        "latency_ms","cache_hit","prefix_len"
    ])
    ev.writeheader()

    summary = {
        "scenario": scenario,
        "use_cache": use_cache,
        "ticks": ticks,
        "seed": seed,
        "count": 0,
        "t_first_ns": None,
        "t_last_ns": None,
        "sum_latency_ms": 0.0,
        "p50_ms": None,
        "p95_ms": None,
        "p99_ms": None,
        "throughput_eps": None,
        "hit_rate": None,
    }
    lat_samples = []
    hits = 0

    def _patched_execute(task):
        # 记录 cache 预判（完全命中时，scheduler 会直接返回）
        prefix_len, hit_val = (0, None)
        try:
            prefix_len, hit_val = dsl.cache.get_with_lmp(task.prompt)
        except Exception:
            prefix_len, hit_val = 0, None
        full_hit = 1 if (hit_val is not None and prefix_len == len(task.prompt)) else 0

        t0 = time.perf_counter_ns()
        try:
            return orig_exec(task)
        finally:
            t1 = time.perf_counter_ns()
            latency_ms = (t1 - t0) / 1e6

            # 事件行
            ev.writerow({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "scenario": scenario,
                "agent": task.agent,
                "name": task.name,
                "prompt_len": len(task.prompt),
                "latency_ms": f"{latency_ms:.3f}",
                "cache_hit": full_hit,
                "prefix_len": prefix_len
            })

            # 汇总
            summary["count"] += 1
            lat_samples.append(latency_ms)
            if full_hit:
                hits += 1
            if summary["t_first_ns"] is None:
                summary["t_first_ns"] = t0
            summary["t_last_ns"] = t1

    # 应用猴补丁
    scheduler._execute_task = _patched_execute  # type: ignore

    # ---------- 运行场景 ----------
    if scenario == "city":
        _ = _city_program(dsl, ticks=ticks, seed=seed)  # p_* 用默认即可，保证可比
    elif scenario == "ad":
        _ = _ad_program(dsl, ticks=ticks, seed=seed, p_collision=0.02)
    else:
        raise ValueError("scenario must be one of {city, ad}")

    # 等队列清空（保险）
    time.sleep(0.2)

    # ---------- 关闭并写 summary ----------
    scheduler.shutdown()
    f_ev.close()

    if summary["count"] > 0:
        dur_s = (summary["t_last_ns"] - summary["t_first_ns"]) / 1e9
        summary["throughput_eps"] = summary["count"] / max(1e-9, dur_s)
        lat_sorted = sorted(lat_samples)
        def _pct(p):
            if not lat_sorted:
                return None
            k = max(0, min(len(lat_sorted)-1, int(math.ceil(p*len(lat_sorted)))-1))
            return lat_sorted[k]
        summary["p50_ms"] = _pct(0.50)
        summary["p95_ms"] = _pct(0.95)
        summary["p99_ms"] = _pct(0.99)
        summary["hit_rate"] = hits / summary["count"]

    with open(summary_path, "w", newline="", encoding="utf-8") as f_sum:
        w = csv.DictWriter(f_sum, fieldnames=list(summary.keys()))
        w.writeheader()
        w.writerow(summary)

    print(json.dumps({"outdir": outdir, **summary}, ensure_ascii=False, indent=2))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", choices=["city","ad"], required=True)
    ap.add_argument("--ticks", type=int, default=300)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--outbase", type=str, default="results")
    args = ap.parse_args()

    # 目录
    out_no = os.path.join(args.outbase, f"{args.scenario}_no_cache")
    out_yes = os.path.join(args.outbase, f"{args.scenario}_with_cache")

    print("=== RUN A (NoCache) ===")
    _run_one(args.scenario, args.ticks, args.seed, out_no, use_cache=False)

    print("=== RUN B (WithCache) ===")
    _run_one(args.scenario, args.ticks, args.seed, out_yes, use_cache=True)


if __name__ == "__main__":
    main()
