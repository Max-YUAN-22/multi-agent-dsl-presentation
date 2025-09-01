
import argparse, csv, os
from collections import defaultdict
import matplotlib.pyplot as plt

def load_events(path):
    rows = []
    with open(path, "r") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append({"t_end": float(row["t_end"]), "latency_ms": float(row["latency_ms"]), "cache_hit": int(row["cache_hit"])})
    return rows

def plot_throughput(events, out_png):
    if not events:
        return
    t0 = min(e["t_end"] for e in events)
    buckets = defaultdict(int)
    for e in events:
        sec = int(e["t_end"] - t0)
        buckets[sec] += 1
    xs = sorted(buckets.keys())
    ys = [buckets[x] for x in xs]
    plt.figure()
    plt.plot(xs, ys, marker="o")
    plt.xlabel("time (s since start)")
    plt.ylabel("completed tasks / s")
    plt.title("Throughput over time")
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

def plot_latency_hist(events, out_png):
    if not events:
        return
    lat = [e["latency_ms"] for e in events]
    plt.figure()
    plt.hist(lat, bins=20)
    plt.xlabel("latency (ms)")
    plt.ylabel("count")
    plt.title("Latency distribution")
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

def plot_cache_hit_ma(events, out_png, window=20):
    if not events:
        return
    hits = [e["cache_hit"] for e in events]
    ma = []
    s = 0
    for i, v in enumerate(hits):
        s += v
        if i >= window:
            s -= hits[i-window]
            ma.append(s / window)
        else:
            ma.append(s / (i+1))
    xs = list(range(len(ma)))
    plt.figure()
    plt.plot(xs, ma)
    plt.xlabel("task index")
    plt.ylabel("cache hit rate (moving avg)")
    plt.title(f"Cache hit moving average (window={window})")
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", required=True, help="path to events.csv")
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    ev = load_events(args.events)
    plot_throughput(ev, os.path.join(args.outdir, "throughput.png"))
    plot_latency_hist(ev, os.path.join(args.outdir, "latency_hist.png"))
    plot_cache_hit_ma(ev, os.path.join(args.outdir, "cache_hit_ma.png"))

if __name__ == "__main__":
    main()
