#!/usr/bin/env bash
set -euo pipefail

# --------- Config ----------
PY=python          # 或 python3
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_CITY="$ROOT/results/demo_city"
OUT_AD="$ROOT/results/demo_ad"
EVENTS_CITY="$OUT_CITY/events.csv"
EVENTS_AD="$OUT_AD/events_ad.csv"
MA_CITY=45
MA_AD=60
# ---------------------------

echo "[quick_demo] project root: $ROOT"
cd "$ROOT"

# 简单依赖自检
need() { command -v "$1" >/dev/null 2>&1 || { echo "need '$1' but it's not installed"; exit 1; }; }
need "$PY"
$PY -c "import pandas,matplotlib,numpy; print('[deps] ok: pandas/matplotlib/numpy')" || {
  echo "[deps] 请先安装: pip install pandas matplotlib numpy"
  exit 1
}

mkdir -p "$OUT_CITY" "$OUT_AD"

echo
echo "[1/4] 生成 城市 事件（mock 稳定复现，可改成真实 311）"
PYTHONPATH=. "$PY" analysis/make_events_from_sf311.py \
  --force-mock \
  --minutes 30 \
  --max-cases 400 \
  --out "$EVENTS_CITY"

echo
echo "[2/4] 城市 出图"
PYTHONPATH=. "$PY" analysis/plot_rt_with_annotations.py \
  --events "$EVENTS_CITY" \
  --outdir "$OUT_CITY" \
  --title "Smart City Multi-Agent DSL — Real-Time Metrics" \
  --source "synthetic (mock)" \
  --window "last 30 min" \
  --city "San Francisco" \
  --ma-window $MA_CITY \
  --annot-peaks

echo
echo "[3/4] 生成 自动驾驶 事件（模拟拥塞/严重度/绕行成本）"
PYTHONPATH=. "$PY" analysis/make_events_autodrive.py \
  --minutes 20 \
  --max-cases 500 \
  --out "$EVENTS_AD"

echo
echo "[4/4] 自动驾驶 出图"
PYTHONPATH=. "$PY" analysis/plot_ad_with_annotations.py \
  --events "$EVENTS_AD" \
  --outdir "$OUT_AD" \
  --title "Autonomous Driving — RT Metrics" \
  --title-sub "Simulated congestion + severity + reroute costs" \
  --source "simulator (agent+cache)" \
  --window "last 20 min" \
  --ma-window $MA_AD \
  --annot-peaks --export-extra

echo
echo "========================================"
echo "[DONE] 结果输出目录："
echo "  City: $OUT_CITY"
echo "    - throughput.png"
echo "    - latency_hist.png"
echo "    - cache_hit_ma.png"
echo "  AD:   $OUT_AD"
echo "    - throughput.png"
echo "    - latency_hist.png"
echo "    - cache_hit_ma.png"
echo "    - event_type_share.png"
echo "    - clearance_reroute_cdf.png"
echo "  元信息：meta.json（两目录各有一份）"
echo "========================================"

# macOS 可自动预览（可选）
if [[ "$OSTYPE" == "darwin"* ]]; then
  echo "[open] 尝试在 macOS 预览关键图..."
  open "$OUT_CITY/throughput.png" "$OUT_CITY/cache_hit_ma.png" 2>/dev/null || true
  open "$OUT_AD/latency_hist.png" "$OUT_AD/cache_hit_ma.png" 2>/dev/null || true
fi
