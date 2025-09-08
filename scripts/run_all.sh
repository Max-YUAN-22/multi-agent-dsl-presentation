#!/usr/bin/env bash
set -e

OUTDIR_BASE="results"

echo "Running Smart City (simulated)..."
PYTHONPATH=. python cli.py city --ticks 50 --p-fall 0.05 --p-moisture 0.05 --seed 1

echo "Running Autonomous Driving (simulated)..."
PYTHONPATH=. python cli.py ad --ticks 50 --p-collision 0.05 --seed 2

echo "Running Smart City (real data, SF311 + Open-Meteo)..."
PYTHONPATH=. python cli.py city_rt --minutes 60 --max-cases 200 --outdir ${OUTDIR_BASE}/city_rt_figs

echo "Running Autonomous Driving (real data, OSM + Open-Meteo)..."
PYTHONPATH=. python cli.py ad_rt --outdir ${OUTDIR_BASE}/ad_rt_figs

echo "Generating annotated plots for Smart City real-time..."
cp ${OUTDIR_BASE}/city_rt_figs/events.csv .
PYTHONPATH=. python analysis/plot_rt_with_annotations.py \
  --events events.csv \
  --outdir ${OUTDIR_BASE}/city_rt_figs \
  --title "Smart City RT Demo" \
  --source "SF311 + Open-Meteo" \
  --window "last 60 min" \
  --city "San Francisco (37.7749,-122.4194)"

echo "Generating annotated plots for Autonomous Driving real-time..."
cp ${OUTDIR_BASE}/ad_rt_figs/events.csv .
PYTHONPATH=. python analysis/plot_rt_with_annotations.py \
  --events events.csv \
  --outdir ${OUTDIR_BASE}/ad_rt_figs \
  --title "Autonomous Driving RT Demo" \
  --source "OSM Overpass + Open-Meteo" \
  --window "last 60 min" \
  --bbox "37.76,-122.46,37.80,-122.39"

echo "✅ All experiments finished. Check results/ folder."
