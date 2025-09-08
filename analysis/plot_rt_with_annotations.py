# analysis/plot_rt_with_annotations.py
import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta

def load_events(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")
    return df

def moving_average(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=1, center=True).mean()

def plot_metrics(df: pd.DataFrame, outdir: str, title: str, title_sub: str,
                 source: str, window: str, city: str, ma_window: int,
                 annot_peaks: bool):
    os.makedirs(outdir, exist_ok=True)

    # ========== Throughput ==========
    counts = df.set_index("timestamp").resample("1min").size()
    counts_ma = moving_average(counts, ma_window)

    fig, ax = plt.subplots(figsize=(10, 5))
    counts.plot(ax=ax, alpha=0.4, label="Raw")
    counts_ma.plot(ax=ax, linewidth=2, label=f"MA({ma_window})")
    ax.set_title(f"{title}\nThroughput — {title_sub}", fontsize=14)
    ax.set_xlabel("Time")
    ax.set_ylabel("Events per min")
    ax.legend()
    ax.grid(True, alpha=0.3)

    if annot_peaks and not counts_ma.empty:
        peak_idx = counts_ma.idxmax()
        peak_val = counts_ma.max()
        ax.annotate(f"Peak: {int(peak_val)}",
                    xy=(peak_idx, peak_val),
                    xytext=(peak_idx + timedelta(minutes=3), peak_val + 1),
                    arrowprops=dict(arrowstyle="->", color="red"),
                    fontsize=10, color="red")

    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "throughput.png"))
    plt.close(fig)

    # ========== Latency ==========
    fig, ax = plt.subplots(figsize=(10, 5))
    df["latency_ms"].plot(kind="hist", bins=30, alpha=0.7, ax=ax)
    ax.set_title(f"{title}\nLatency Distribution — {title_sub}", fontsize=14)
    ax.set_xlabel("Latency (ms)")
    ax.set_ylabel("Frequency")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "latency_hist.png"))
    plt.close(fig)

    # ========== Cache Hit ==========
    hits = df.set_index("timestamp")["cache_hit"].resample("1min").mean()
    hits_ma = moving_average(hits, ma_window)

    fig, ax = plt.subplots(figsize=(10, 5))
    hits.plot(ax=ax, alpha=0.4, label="Raw")
    hits_ma.plot(ax=ax, linewidth=2, label=f"MA({ma_window})")
    ax.set_title(f"{title}\nCache Hit Rate — {title_sub}", fontsize=14)
    ax.set_xlabel("Time")
    ax.set_ylabel("Cache Hit Rate")
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "cache_hit_ma.png"))
    plt.close(fig)

def main(events_csv: str, outdir: str, title: str, source: str,
         window: str, city: str, ma_window: int,
         annot_peaks: bool, title_sub: str):
    df = load_events(events_csv)
    if df.empty:
        print(f"No events found in {events_csv}, skipping plot generation.")
        return
    plot_metrics(df, outdir, title, title_sub, source, window, city,
                 ma_window, annot_peaks)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", required=True, help="Event CSV file")
    ap.add_argument("--outdir", required=True, help="Output directory for charts")
    ap.add_argument("--title", type=str, default="Smart City Metrics")
    ap.add_argument("--source", type=str, default="synthetic/mock")
    ap.add_argument("--window", type=str, default="last X min")
    ap.add_argument("--city", type=str, default="Unknown City")
    ap.add_argument("--bbox", type=str, help="Bounding box for the map area")
    ap.add_argument("--ma-window", type=int, default=30)
    ap.add_argument("--annot-peaks", action="store_true")
    ap.add_argument("--title-sub", type=str, default="RT Metrics")

    args = ap.parse_args()
    main(args.events, args.outdir, args.title, args.source,
         args.window, args.city, args.ma_window,
         args.annot_peaks, args.title_sub)
