# analysis/quick_validate.py
import os, json, argparse
from datetime import datetime
from freezegun import freeze_time

from dsl.dsl import DSL
import agents.city_realtime as city_rt  
from analysis.plot_rt_with_annotations import main as plot_main

@freeze_time("2024-05-01 12:00:00")
def run_quick_city(minutes:int=10, max_cases:int=60, outdir:str="results/quick_demo"):
    dsl = DSL()
    res = city_rt.city_realtime(dsl, minutes=minutes, max_cases=max_cases, outdir=outdir)

    os.makedirs(outdir, exist_ok=True)
    meta = {
        "demo": "quick_city_rt",
        "source": "SF311 + Open-Meteo (no key)",
        "window": f"{minutes}min",
        "params": {"minutes": minutes, "max_cases": max_cases},
        "finished_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "result": res,
    }
    with open(os.path.join(outdir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    events_path = os.path.join(outdir, "events.csv")
    summary_path = os.path.join(outdir, "summary.csv")
    if os.path.exists(events_path):
        plot_main(
            events_csv=events_path,
            outdir=outdir,
            title="Smart City (Quick RT)",
            source="SF311 + Open-Meteo",
            window=f"last {minutes} min",
            city="San Francisco (37.7749,-122.4194)",
            ma_window=30,
            annot_peaks=False,
            title_sub="RT Metrics"
        )
    else:
        print("[quick] No events.csv found. Skipping plots from CSV.")

    print({"ok": True, "outdir": outdir, "summary": res})
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser("quick-validate")
    ap.add_argument("--minutes", type=int, default=10)
    ap.add_argument("--max-cases", type=int, default=60)
    ap.add_argument("--outdir", type=str, default="results/quick_demo")
    args = ap.parse_args()
    run_quick_city(args.minutes, args.max_cases, args.outdir)
