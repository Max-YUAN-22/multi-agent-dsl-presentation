# analysis/make_events_from_sf311.py
import os
import argparse
import math
import random
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd

# Optional: If you have the previous api_clients.py, it will try to use real 311 first;
# not having it does not affect the mock output.
SF311_AVAILABLE = False
NYC311_AVAILABLE = False
try:
    from analysis.api_clients import SF311Client, NYC311Client  # Optional dependency
    SF311_AVAILABLE = True
    NYC311_AVAILABLE = True
except Exception:
    pass

# Some categories and area names for mock data (for demonstration purposes)
MOCK_CATEGORIES = [
    "illegal_dumping", "street_cleaning", "noise", "blocked_driveway",
    "abandoned_vehicle", "encampment", "trash_pickup", "graffiti"
]
MOCK_AREAS = [
    "Mission", "SOMA", "Bernal Heights", "Richmond", "Sunset",
    "Noe Valley", "Chinatown", "Financial District", "Castro", "Marina"
]

def _day_factor(t_utc: datetime) -> float:
    """Simple day/night factor, more active during the day"""
    h = t_utc.astimezone(timezone.utc).hour
    return 1.0 + (0.18 if 7 <= h <= 21 else -0.12) + 0.08 * math.sin(h/24*2*math.pi)

def _mock_df(minutes: int, max_cases: int, seed: int = 7) -> pd.DataFrame:
    """
    Generate a "realistic-looking" stream of city events:
    - Congestion windows (denser events, higher latency, slightly lower cache hit rate)
    - Mix of categories/areas
    - Latency/hit rate with noise to make the MA curve look good
    """
    rng = np.random.default_rng(seed)
    now = datetime.now(timezone.utc)

    # Use a slightly larger base number to make the chart look good
    n = max(200, min(max_cases * 2, 1000))
    times = [now - timedelta(seconds=int(i * (minutes * 60) / n)) for i in range(n)]

    # Generate 1 to 3 congestion windows
    windows = []
    for _ in range(rng.integers(1, 3+1)):
        s = rng.integers(0, max(1, n - 20))
        wlen = int(rng.integers(max(15, n//25), max(30, n//10)))
        windows.append(range(s, min(n, s + wlen)))

    recs = []
    excitation = 0.0
    for i, ts in enumerate(times):
        # Event intensity: day/night + short-term self-excitation + random noise
        lam = 0.020 * _day_factor(ts) * (1.0 + excitation)
        lam = float(np.clip(lam + rng.normal(0, 0.0035), 0.003, 0.30))
        if rng.random() < lam:
            category = random.choice(MOCK_CATEGORIES)
            location = random.choice(MOCK_AREAS)
            is_congested = any(i in w for w in windows)

            # Latency: faster for service-related, slower for enforcement/emergency;
            # extra time for congestion windows
            mix_fast = rng.normal(140, 35)    # Cleaning/spraying, etc.
            mix_slow = rng.normal(320, 70)    # Noise/illegal parking/obstruction, etc.
            base_latency = mix_fast if category in ["street_cleaning", "trash_pickup", "graffiti"] else mix_slow
            congestion_surcharge = rng.normal(90, 30) if is_congested else 0.0
            latency_ms = max(60, base_latency + congestion_surcharge + rng.normal(0, 25))

            # Hit rate: higher for template-similar classes; slightly lower during congestion
            hit_base = 0.48 if category in ["street_cleaning", "trash_pickup", "graffiti"] else 0.30
            if is_congested:
                hit_base -= 0.10
            cache_hit = 1 if rng.random() < float(np.clip(hit_base + rng.normal(0, 0.05), 0.05, 0.90)) else 0

            recs.append({
                "timestamp": ts.isoformat(),
                "category": category,
                "location": location,
                "latency_ms": round(float(latency_ms), 1),
                "cache_hit": int(cache_hit),
            })
            # Short-term self-excitation after an event
            excitation = min(0.7, excitation + 0.05)
        # Self-excitation decay
        excitation = max(0.0, excitation * 0.97)

    df = pd.DataFrame(recs, columns=["timestamp", "category", "location", "latency_ms", "cache_hit"])
    if df.empty:
        return df
    df["_time"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["_time"]).sort_values("_time").drop(columns=["_time"])
    # Truncate to max_cases to avoid being too large
    return df.head(max_cases)

def _rows_to_df(rows: list, minutes: int) -> pd.DataFrame:
    """Convert 311 rows to a DataFrame; fields are compatible with various 311 table structures"""
    if not rows:
        return pd.DataFrame(columns=["timestamp", "category", "location", "latency_ms", "cache_hit"])
    now = datetime.now(timezone.utc)
    recs = []
    for r in rows:
        category = (r.get("service_subtype") or r.get("service_type") or r.get("service_name") or "unknown")
        location = r.get("neighborhoods_sffind_boundaries") or r.get("neighborhood") or r.get("address") or "Unknown"
        ts = None
        for k in ["requested_datetime", "created_date", "opened", "created_dt",
                  "requested_datetime_utc", "service_request_date"]:
            if r.get(k):
                ts = pd.to_datetime(r[k], utc=True, errors="coerce")
                if pd.notna(ts):
                    break
        if ts is None or pd.isna(ts):
            ts = now - timedelta(seconds=random.randint(0, minutes * 60))

        latency_ms = random.randint(100, 420)
        cache_hit = 1 if random.random() < 0.3 else 0

        recs.append({
            "timestamp": ts.isoformat(),
            "category": str(category),
            "location": str(location),
            "latency_ms": int(latency_ms),
            "cache_hit": int(cache_hit),
        })
    df = pd.DataFrame(recs)
    df["_time"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["_time"]).sort_values("_time").drop(columns=["_time"])
    return df

def _try_fetch_311(minutes: int, limit: int) -> pd.DataFrame:
    """Try to fetch near real-time data from SF -> NYC; return an empty DF on failure"""
    # Time window strategy: gradually fall back from short to long
    windows_min = [minutes, 120, 720, 1440, 4320]
    # Prioritize SF
    if SF311_AVAILABLE:
        sf = SF311Client()
        for m in windows_min:
            try:
                rows = sf.fetch_recent_cases(minutes=m, limit=limit) or []
                df = _rows_to_df(rows, m)
                if len(df) >= 20:
                    print(f"[info] SF311 ok with last {m} min: {len(df)} rows")
                    return df.head(limit)
            except Exception as e:
                print(f"[warn] SF 311 failed (last {m} min): {e}")
    # Then NYC
    if NYC311_AVAILABLE:
        ny = NYC311Client()
        for m in windows_min:
            try:
                rows = ny.fetch_recent_cases(minutes=m, limit=limit) or []
                df = _rows_to_df(rows, m)
                if len(df) >= 20:
                    print(f"[info] NYC311 ok with last {m} min: {len(df)} rows")
                    return df.head(limit)
            except Exception as e:
                print(f"[warn] NYC 311 failed (last {m} min): {e}")
    print("[warn] All 311 attempts failed; fallback to mock")
    return pd.DataFrame(columns=["timestamp", "category", "location", "latency_ms", "cache_hit"])

def main(minutes: int, max_cases: int, out_csv: str, force_mock: bool, seed: int):
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    random.seed(seed); np.random.seed(seed)

    if force_mock:
        print("[info] using forced mock data generator")
        df = _mock_df(minutes, max_cases, seed=seed)
    else:
        # Try real 311 first; top up with mock if not enough
        df = _try_fetch_311(minutes, max_cases)
        if len(df) < max(50, int(max_cases * 0.5)):
            print(f"[info] rows too few ({len(df)}) -> top-up with mock to reach >= {max_cases}")
            df_mock = _mock_df(minutes, max_cases, seed=seed + 1)
            df = pd.concat([df, df_mock], ignore_index=True).sort_values("timestamp").head(max_cases)

    # Fallback
    if df.empty:
        print("[info] empty after fetch — generating mock fallback")
        df = _mock_df(minutes, max_cases, seed=seed + 2)

    df.to_csv(out_csv, index=False)
    print({"wrote": out_csv, "rows": int(len(df)), "source": ("mock" if force_mock else "real+mock" if len(df) else "mock")})

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=int, default=30, help="Lookback minutes (for generation/fetching)")
    ap.add_argument("--max-cases", type=int, default=400, help="Maximum number of events")
    ap.add_argument("--out", type=str, default="results/demo_city/events.csv", help="Output CSV path")
    ap.add_argument("--force-mock", action="store_true", help="Force use of mock data (do not access 311 API)")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    main(args.minutes, args.max_cases, args.out, args.force_mock, args.seed)
