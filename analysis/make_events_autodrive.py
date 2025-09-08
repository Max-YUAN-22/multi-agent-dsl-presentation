# analysis/make_events_autodrive.py
import os, argparse, math, random
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd

# Road and event types (can be extended as needed)
ROAD_EDGES = [f"E{i}-{j}" for i in range(1, 7) for j in range(1, 7)]
EVENT_TYPES = [
    "collision_minor","collision_major","near_miss",
    "stalled_vehicle","road_obstruction","road_closure"
]

def _day_factor(t_utc: datetime) -> float:
    """Simple day/night factor, events are more frequent during the day"""
    h = t_utc.astimezone(timezone.utc).hour
    return 1.0 + (0.22 if 7 <= h <= 21 else -0.12) + 0.10 * math.sin(h/24*2*math.pi)

def _mock_autodrive_df(minutes: int, max_cases: int, scale: float, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    base_n = int(np.clip(220 * scale, 200, max(220, max_cases*2)))  # Ensure sufficient sampling
    now = datetime.now(timezone.utc)
    times = [now - timedelta(seconds=int(i * (minutes * 60) / base_n)) for i in range(base_n)]

    # Randomly generate several congestion windows (exponential/Gaussian superposition)
    windows = []
    for _ in range(rng.integers(1, 4)):
        s = rng.integers(0, max(1, base_n - 20))
        wlen = int(rng.integers(max(12, base_n//25), max(25, base_n//10)))
        windows.append(range(s, min(base_n, s + wlen)))

    recs, excitation = [], 0.0
    for i, ts in enumerate(times):
        # Event occurrence probability (including day/night, short-term excitation noise)
        lam = 0.018 * _day_factor(ts) * (1.0 + excitation)
        lam = float(np.clip(lam + rng.normal(0, 0.0035), 0.004, 0.30))
        if rng.random() < lam:
            road = random.choice(ROAD_EDGES)
            et = random.choices(EVENT_TYPES, weights=[0.25,0.08,0.28,0.18,0.14,0.07], k=1)[0]
            is_cong = any(i in w for w in windows)

            # Processing delay (different event baselines + congestion surcharge)
            base_delay_mu_sd = {
                "near_miss": (120, 35),
                "stalled_vehicle": (240, 55),
                "road_obstruction": (320, 70),
                "collision_minor": (380, 90),
                "collision_major": (520, 120),
                "road_closure": (460, 100),
            }[et]
            mu, sd = base_delay_mu_sd
            cong_add = rng.normal(120, 35) if is_cong else 0.0
            agent_latency_ms = max(70.0, rng.normal(mu, sd) + cong_add + rng.normal(0, 20))

            # Lane occupancy & involved vehicle estimation
            lanes_blocked = {
                "near_miss":0,"stalled_vehicle":1,"road_obstruction":1,
                "collision_minor":int(rng.integers(1,3)),
                "collision_major":int(rng.integers(2,4)),
                "road_closure":3
            }[et]
            vehicles = {
                "near_miss":int(rng.integers(1,3)),
                "stalled_vehicle":1,
                "road_obstruction":int(rng.integers(1,2)),
                "collision_minor":int(rng.integers(2,3)),
                "collision_major":int(rng.integers(3,5)),
                "road_closure":0
            }[et]

            # Severity (1-5)
            sev_base = {
                "near_miss":1.5,"stalled_vehicle":2.0,"road_obstruction":2.5,
                "collision_minor":3.0,"collision_major":4.3,"road_closure":3.8
            }[et]
            severity = int(np.clip(round(rng.normal(sev_base + (0.5 if is_cong else 0.0), 0.9)), 1, 5))

            # Cache hit rate (higher for template-similar classes; decreases during congestion)
            hit_base = {
                "near_miss":0.55,"stalled_vehicle":0.42,"road_obstruction":0.35,
                "collision_minor":0.32,"collision_major":0.22,"road_closure":0.25
            }[et]
            if is_cong: hit_base -= 0.12
            cache_hit = 1 if rng.random() < float(np.clip(hit_base + rng.normal(0,0.05), 0.05, 0.9)) else 0

            # Clearance time / rerouting cost (seconds)
            clearance_mu = {
                "near_miss":60,"stalled_vehicle":8*60,"road_obstruction":12*60,
                "collision_minor":18*60,"collision_major":40*60,"road_closure":30*60
            }[et]
            clearance_time_s = max(20, rng.normal(clearance_mu * (1.15 if is_cong else 1.0), clearance_mu * 0.2))
            reroute_delay_s = max(0, rng.normal({
                "near_miss":10,"stalled_vehicle":45,"road_obstruction":70,
                "collision_minor":120,"collision_major":300,"road_closure":240
            }[et] * (1.2 if lanes_blocked >= 2 else 1.0), 25))

            recs.append({
                "timestamp": ts.isoformat(),
                "road": road,
                "event_type": et,
                "severity": int(severity),
                "vehicles": int(vehicles),
                "lanes_blocked": int(lanes_blocked),
                "agent_latency_ms": round(float(agent_latency_ms),1),
                "cache_hit": int(cache_hit),
                "clearance_time_s": round(float(clearance_time_s),1),
                "reroute_delay_s": round(float(reroute_delay_s),1),
                "is_congested": int(1 if is_cong else 0),
            })
            # Short-term self-excitation after event
            excitation = min(0.7, excitation + 0.05)
        # Self-excitation decay
        excitation = max(0.0, excitation * 0.97)

    df = pd.DataFrame(recs)
    if df.empty:
        return df
    df["_t"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("_t").drop(columns=["_t"])
    return df

def main(minutes: int, max_cases: int, out_csv: str, mock_scale: float, seed: int):
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    random.seed(seed)
    np.random.seed(seed)

    df = _mock_autodrive_df(minutes, max_cases, mock_scale, seed)

    # Ensure at least 200 rows to prevent sparse plots in small windows
    if len(df) < 200:
        extra = _mock_autodrive_df(minutes, max(220 - len(df), 80), mock_scale, seed + 1)
        df = pd.concat([df, extra], ignore_index=True).sort_values("timestamp")

    df = df.head(max_cases)
    df.to_csv(out_csv, index=False)
    print({"wrote": out_csv, "rows": len(df)})

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=int, default=20)
    ap.add_argument("--max-cases", type=int, default=500)
    ap.add_argument("--out", type=str, default="results/demo_ad/events_ad.csv")
    ap.add_argument("--mock-scale", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    main(args.minutes, args.max_cases, args.out, args.mock_scale, args.seed)
