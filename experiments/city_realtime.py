# experiments/city_realtime.py
from dsl.dsl import DSL
from agents.city_realtime import city_realtime
import os, json, argparse
from datetime import datetime

def main(minutes: int = 60, max_cases: int = 200, outdir: str = "results/city_rt"):
    dsl = DSL()
    res = city_realtime(dsl, minutes=minutes, max_cases=max_cases, outdir=outdir)
    os.makedirs(outdir, exist_ok=True)
    meta = {
        "demo": "city_rt",
        "source": "SF311 + Open-Meteo (no key)",
        "window": f"{minutes}min",
        "city": "San Francisco (37.7749,-122.4194)",
        "params": {"minutes": minutes, "max_cases": max_cases},
        "finished_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "result": res,
    }
    with open(os.path.join(outdir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=int, default=60)
    ap.add_argument("--max-cases", type=int, default=200)
    ap.add_argument("--outdir", type=str, default="results/city_rt")
    args = ap.parse_args()
    print(main(args.minutes, args.max_cases, args.outdir))
