# experiments/ad_realtime.py
from dsl.dsl import DSL
from agents.ad_realtime import ad_realtime
import os, json, argparse
from datetime import datetime

def main(outdir: str = "results/ad_rt"):
    dsl = DSL()
    res = ad_realtime(dsl, outdir=outdir)
    os.makedirs(outdir, exist_ok=True)
    meta = {
        "demo": "ad_rt",
        "source": "Overpass(OSM) + Open-Meteo (no key)",
        "bbox": "SF (37.76,-122.46,37.80,-122.39)",
        "params": {},
        "finished_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "result": res,
    }
    with open(os.path.join(outdir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", type=str, default="results/ad_rt")
    args = ap.parse_args()
    print(main(args.outdir))
