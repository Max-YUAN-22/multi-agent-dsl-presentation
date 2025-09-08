#!/usr/bin/env bash
set -e

# Small, fast demo (5–10 min window)
PYTHONPATH=. python analysis/quick_validate.py \
  --minutes 10 \
  --max-cases 60 \
  --outdir results/quick_demo

echo "✅ Quick demo done. See results/quick_demo/:"
ls -l results/quick_demo || true

