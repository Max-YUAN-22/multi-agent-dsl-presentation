# analysis/plot_ad_with_annotations.py
import os, argparse, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def moving_average(x: pd.Series, w: int) -> pd.Series:
    if w <= 1:
        return x.copy()
    return x.rolling(window=w, min_periods=1, center=False).mean()

def load_events(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    if "timestamp" not in df.columns:
        raise ValueError("CSV must contain a 'timestamp' column")
    df["_time"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["_time"]).sort_values("_time")
    return df

def _savefig(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()

def _plot_cdf(ax, series: pd.Series, label: str):
    v = np.sort(series.dropna().astype(float).values)
    if len(v) == 0:
        return False
    y = np.linspace(0, 1, len(v))
    ax.plot(v, y, label=label)
    return True

def main(events_csv: str, outdir: str, title: str, title_sub: str, source: str,
         window: str, ma_window: int, annot_peaks: bool, export_extra: bool):
    os.makedirs(outdir, exist_ok=True)
    df = load_events(events_csv)
    if df.empty:
        print("[warn] empty events csv — nothing to plot.")
        return

    # Unify time index (second level)
    idx = pd.date_range(df["_time"].min().floor("s"),
                        df["_time"].max().ceil("s"),
                        freq="s")

    # 1) Throughput (events/sec)
    s_cnt = df.set_index("_time").assign(cnt=1)["cnt"].resample("s").sum().reindex(idx, fill_value=0)
    s_ma = moving_average(s_cnt, ma_window).bfill().ffill()

    plt.figure(figsize=(10, 4))
    plt.plot(s_cnt.index, s_cnt.values, alpha=0.6, label="events/sec")
    plt.plot(s_ma.index, s_ma.values, linestyle="--", label=f"MA({ma_window})")
    ttl = title if not title_sub else f"{title}\n{title_sub}"
    plt.title(ttl)
    plt.xlabel(f"Time | {window} | {source}")
    plt.ylabel("Throughput (events/sec)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    if annot_peaks and len(s_cnt) > 0:
        peaks = np.argsort(s_cnt.values)[-3:]
        for i in peaks:
            t, v = s_cnt.index[i], s_cnt.values[i]
            plt.annotate(f"peak {int(v)}", xy=(t, v), xytext=(0, 10),
                         textcoords="offset points", fontsize=9)
    p1 = os.path.join(outdir, "throughput.png")
    _savefig(p1)

    # 2) Agent latency histogram
    latency_col = "agent_latency_ms" if "agent_latency_ms" in df.columns else "latency_ms"
    p2 = None
    if latency_col in df.columns:
        plt.figure(figsize=(10, 4))
        plt.hist(df[latency_col].values, bins=40, alpha=0.75)
        plt.title("Agent processing latency (ms)")
        plt.xlabel("Latency (ms)"); plt.ylabel("Count")
        plt.grid(True, alpha=0.3)
        p2 = os.path.join(outdir, "latency_hist.png")
        _savefig(p2)

    # 3) Cache hit ratio over time
    p3 = None
    if "cache_hit" in df.columns:
        hit_series = df.set_index("_time")["cache_hit"].resample("s").mean().reindex(idx, fill_value=np.nan).bfill().ffill()
        hit_ma = moving_average(hit_series, ma_window).bfill().ffill()
        plt.figure(figsize=(10, 4))
        plt.plot(hit_series.index, hit_series.values, alpha=0.5, label="hit ratio (sec)")
        plt.plot(hit_ma.index, hit_ma.values, linestyle="--", label=f"MA({ma_window})")
        plt.ylim(0, 1.0)
        plt.title("Cache hit ratio over time")
        plt.xlabel("Time"); plt.ylabel("Hit ratio")
        plt.legend(); plt.grid(True, alpha=0.3)
        p3 = os.path.join(outdir, "cache_hit_ma.png")
        _savefig(p3)

    extras = []
    if export_extra:
        # 4) Event type share (pie)
        if "event_type" in df.columns:
            plt.figure(figsize=(7, 7))
            (df["event_type"].value_counts(normalize=True)*100.0).sort_values(ascending=False)\
                .plot(kind="pie", autopct="%1.1f%%")
            plt.title("Event type composition")
            extras.append(os.path.join(outdir, "event_type_share.png"))
            _savefig(extras[-1])

        # 5) Clearance & Reroute CDF
        cdf_any = False
        fig, ax = plt.subplots(figsize=(9, 4))
        if "clearance_time_s" in df.columns:
            cdf_any |= _plot_cdf(ax, df["clearance_time_s"], "clearance (s)")
        if "reroute_delay_s" in df.columns:
            cdf_any |= _plot_cdf(ax, df["reroute_delay_s"], "reroute delay (s)")
        if cdf_any:
            ax.set_xlabel("Seconds"); ax.set_ylabel("CDF"); ax.legend()
            ax.set_title("Clearance & Reroute CDF"); ax.grid(True, alpha=0.3)
            extras.append(os.path.join(outdir, "clearance_reroute_cdf.png"))
            _savefig(extras[-1])
        else:
            plt.close(fig)

    meta = {
        "events_csv": events_csv,
        "outdir": outdir,
        "figures": [p for p in [p1, p2, p3] if p] + extras,
        "ma_window": ma_window,
        "n_events": int(len(df)),
        "columns": df.columns.tolist(),
    }
    with open(os.path.join(outdir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print("Plots saved:", meta)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--title", default="Autonomous Driving — RT Metrics")
    ap.add_argument("--title-sub", default="Simulated congestion + severity + reroute costs")
    ap.add_argument("--source", default="simulator (agent+cache)")
    ap.add_argument("--window", default="last window")
    ap.add_argument("--ma-window", type=int, default=60)
    ap.add_argument("--annot-peaks", action="store_true")
    ap.add_argument("--export-extra", action="store_true")
    args = ap.parse_args()

    main(events_csv=args.events, outdir=args.outdir, title=args.title,
         title_sub=args.title_sub, source=args.source, window=args.window,
         ma_window=args.ma_window, annot_peaks=args.annot_peaks, export_extra=args.export_extra)
