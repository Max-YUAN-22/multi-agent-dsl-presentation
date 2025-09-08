# -*- coding: utf-8 -*-
import os, argparse, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def _must_exists(p):
    if not os.path.exists(p):
        print(f"[error] missing file: {p}", file=sys.stderr); sys.exit(2)

def _read(path):
    ev_path = os.path.join(path, "events.csv")
    sm_path = os.path.join(path, "summary.csv")
    _must_exists(ev_path); _must_exists(sm_path)

    ev = pd.read_csv(ev_path)
    if "timestamp" not in ev.columns:
        print(f"[error] {ev_path} has no 'timestamp' column; run_ab likely crashed early.", file=sys.stderr)
        sys.exit(2)
    # Unify column types
    ev["_time"] = pd.to_datetime(ev["timestamp"], utc=True, errors="coerce")
    ev = ev.dropna(subset=["_time"]).sort_values("_time").reset_index(drop=True)

    # Force cache_hit to be numeric (fallback for string/boolean), fill with 0 on error
    if "cache_hit" in ev.columns:
        ev["cache_hit"] = pd.to_numeric(ev["cache_hit"], errors="coerce").fillna(0.0).clip(0,1)
    else:
        ev["cache_hit"] = 0.0

    # Also convert latency to numeric
    if "latency_ms" in ev.columns:
        ev["latency_ms"] = pd.to_numeric(ev["latency_ms"], errors="coerce")
    else:
        ev["latency_ms"] = np.nan

    sm = pd.read_csv(sm_path)
    return ev, (sm.iloc[0].to_dict() if len(sm) else {})

def _sec_index(ev):
    if ev.empty: 
        return pd.DatetimeIndex([])
    return pd.date_range(ev["_time"].min().floor("s"), ev["_time"].max().ceil("s"), freq="s")

def _per_sec(ev, col, agg):
    if ev.empty: 
        return pd.Series(dtype=float)
    s = ev.set_index("_time")[col].resample("s")
    if agg == "count": g = s.count()
    elif agg == "mean": g = s.mean()
    elif agg == "sum": g = s.sum()
    else: raise ValueError
    return g.reindex(_sec_index(ev), fill_value=0 if agg in ("count","sum") else np.nan)

def _ma(s, w=15):
    if s.empty: return s
    return s.rolling(window=w, min_periods=1).mean()

def plot_all(with_ev, with_sm, no_ev, no_sm, outdir, title):
    os.makedirs(outdir, exist_ok=True)

    # 1) Throughput (events/sec, MA10)
    t_with = _per_sec(with_ev, "name", "count")
    t_no   = _per_sec(no_ev,   "name", "count")

    if t_with.empty and t_no.empty:
        print("[error] both sides have no events after timestamp parsing; abort.", file=sys.stderr); sys.exit(2)

    plt.figure(figsize=(8,4.2))
    if not t_no.empty:   plt.plot(t_no.index,   _ma(t_no,   10), label="NoCache (MA10)")
    if not t_with.empty: plt.plot(t_with.index, _ma(t_with, 10), label="WithCache (MA10)")
    plt.xlabel("Time (UTC)"); plt.ylabel("Events / sec"); plt.title(f"{title} — Throughput")
    plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(outdir, "throughput_ab.png"), dpi=160); plt.close()

    # 2) Latency Histogram (overlay)
    plt.figure(figsize=(6.8,4.2))
    if not no_ev.empty and no_ev["latency_ms"].notna().any():
        plt.hist(no_ev["latency_ms"].dropna(), bins=40, alpha=0.6, label="NoCache")
    if not with_ev.empty and with_ev["latency_ms"].notna().any():
        plt.hist(with_ev["latency_ms"].dropna(), bins=40, alpha=0.6, label="WithCache")
    plt.xlabel("Latency (ms)"); plt.ylabel("Count"); plt.title(f"{title} — Latency Histogram")
    plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(outdir, "latency_hist_ab.png"), dpi=160); plt.close()

    # 3) Cache hit rate: calculated as "hits per second / total per second" (more robust than a simple mean)
    with_hit = _per_sec(with_ev.assign(is_hit=(with_ev["cache_hit"]>0).astype(int)), "is_hit", "sum")
    with_cnt = _per_sec(with_ev, "name", "count")
    no_hit   = _per_sec(no_ev.assign(is_hit=(no_ev["cache_hit"]>0).astype(int)), "is_hit", "sum")
    no_cnt   = _per_sec(no_ev, "name", "count")

    with_rate = (with_hit / with_cnt.replace(0, np.nan)).fillna(0.0)
    no_rate   = (no_hit   / no_cnt.replace(0, np.nan)).fillna(0.0)

    plt.figure(figsize=(8,4.2))
    if not no_rate.empty:   plt.plot(no_rate.index,   _ma(no_rate,   30), label="NoCache (MA30)")
    if not with_rate.empty: plt.plot(with_rate.index, _ma(with_rate, 30), label="WithCache (MA30)")
    plt.ylim(0,1.0); plt.xlabel("Time (UTC)"); plt.ylabel("Cache Hit Rate")
    plt.title(f"{title} — Cache Hit (MA)"); plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(outdir, "cache_hit_ab.png"), dpi=160); plt.close()

    # Summary
    with open(os.path.join(outdir, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        if with_sm: f.write(f"- WithCache: throughput ≈ {with_sm.get('throughput_eps',0):.2f} eps, hit_rate ≈ {with_sm.get('hit_rate',0):.3f}\n")
        if no_sm:   f.write(f"- NoCache:   throughput ≈ {no_sm.get('throughput_eps',0):.2f} eps, hit_rate ≈ {no_sm.get('hit_rate',0):.3f}\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir-with", required=True)
    ap.add_argument("--indir-no",   required=True)
    ap.add_argument("--outdir",     required=True)
    ap.add_argument("--title",      default="A/B Compare")
    args = ap.parse_args()

    with_ev, with_sm = _read(args.indir_with)
    no_ev,   no_sm   = _read(args.indir_no)
    plot_all(with_ev, with_sm, no_ev, no_sm, args.outdir, args.title)

if __name__ == "__main__":
    main()
