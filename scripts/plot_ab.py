
import argparse, csv, os
import numpy as np
import matplotlib.pyplot as plt

def load_events(path):
    rows = []
    with open(path, "r") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append({"t_end": float(row["t_end"]), "latency_ms": float(row["latency_ms"]), "cache_hit": int(row["cache_hit"])})
    return rows

def throughput_curve(ev, bin_ms=10.0):
    if not ev: return [], []
    t0 = min(e["t_end"] for e in ev)
    dt = [(e["t_end"]-t0)*1000.0 for e in ev]
    bins = np.arange(0, max(dt)+bin_ms, bin_ms)
    counts, edges = np.histogram(dt, bins=bins)
    centers = (edges[:-1]+edges[1:])/2.0
    return centers, counts

def plot_ab(a_path, b_path, outdir):
    os.makedirs(outdir, exist_ok=True)
    A = load_events(a_path)
    B = load_events(b_path)

    # 1) Latency CDF
    def cdf(data):
        x = np.sort([e["latency_ms"] for e in data])
        y = np.arange(1, len(x)+1)/len(x) if len(x) else []
        return x, y

    xa, ya = cdf(A)
    xb, yb = cdf(B)
    plt.figure()
    if len(xa): plt.plot(xa, ya, label="A")
    if len(xb): plt.plot(xb, yb, label="B")
    plt.xlabel("latency (ms)"); plt.ylabel("CDF"); plt.title("Latency CDF (A vs B)"); plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(outdir, "latency_cdf_ab.png")); plt.close()

    # 2) Throughput (10ms bins)
    ca_x, ca_y = throughput_curve(A, 10.0)
    cb_x, cb_y = throughput_curve(B, 10.0)
    plt.figure()
    if len(ca_x): plt.plot(ca_x, ca_y, label="A")
    if len(cb_x): plt.plot(cb_x, cb_y, label="B")
    plt.xlabel("time since start (ms)"); plt.ylabel("completed tasks / 10ms"); plt.title("Throughput (A vs B)"); plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(outdir, "throughput_ab.png")); plt.close()

    # 3) Cache hit cumulative
    def cum_hit(ev):
        if not ev: return [], []
        hits = np.array([e["cache_hit"] for e in ev], dtype=float)
        cum = np.cumsum(hits)/np.arange(1, len(hits)+1)
        x = np.arange(len(hits))
        return x, cum
    xa, ya = cum_hit(A)
    xb, yb = cum_hit(B)
    plt.figure()
    if len(xa): plt.plot(xa, ya, label="A")
    if len(xb): plt.plot(xb, yb, label="B")
    plt.xlabel("task index"); plt.ylabel("cumulative hit rate"); plt.title("Cache hit rate (A vs B)"); plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(outdir, "cache_hit_ab.png")); plt.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="events.csv for A (e.g., no-cache)")
    ap.add_argument("--b", required=True, help="events.csv for B (e.g., with-cache)")
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    plot_ab(args.a, args.b, args.outdir)
