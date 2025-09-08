# analysis/quick_validate_ad.py
import os, json, argparse
from datetime import datetime

from analysis.plot_rt_with_annotations import main as plot_main

def run_quick_ad(minutes:int=20, max_events:int=120, outdir:str="results/quick_demo_ad"):
    os.makedirs(outdir, exist_ok=True)

    # First, generate events.csv (Overpass + Open-Meteo, with automatic mock fallback on error)
    events_csv = os.path.join(outdir, "events.csv")
    import subprocess, sys
    subprocess.check_call([
        sys.executable, "-m", "analysis.make_events_for_ad",
        "--minutes", str(minutes),
        "--max-events", str(max_events),
        "--out", events_csv
    ])

    # Metadata (for reproducibility/reporting)
    meta = {
        "demo": "quick_ad_rt",
        "source": "Overpass(OSM)+Open-Meteo (fallback: mock)",
        "bbox": "SF (37.76,-122.46,37.80,-122.39)",
        "window": f"{minutes}min",
        "params": {"minutes": minutes, "max_events": max_events},
        "finished_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(os.path.join(outdir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    # Call the unified plotting script (with annotations)
    import sys
    sys.argv = [
        "plot_rt_with_annotations.py",
        "--events", events_csv,
        "--outdir", outdir,
        "--title", "Autonomous Driving (Quick RT)",
        "--source", "OSM Overpass + Open-Meteo",
        "--window", f"last {minutes} min",
        "--bbox", "37.76,-122.46,37.80,-122.39",
    ]
    plot_main()

    print({"ok": True, "outdir": outdir})
    return True

if __name__ == "__main__":
    ap = argparse.ArgumentParser("quick-validate-ad")
    ap.add_argument("--minutes", type=int, default=20)
    ap.add_argument("--max-events", type=int, default=120)
    ap.add_argument("--outdir", type=str, default="results/quick_demo_ad")
    args = ap.parse_args()
    run_quick_ad(args.minutes, args.max_events, args.outdir)
