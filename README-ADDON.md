## 🟢 Real-World Data Demos (Annotated)

本框架除了内置的模拟场景，还支持 **接入公开 API 的真实数据流**，零 API Key 即可运行：

### 1. 智慧城市（SF311 + Open-Meteo）
- 命令：
  ```bash
  PYTHONPATH=. python cli.py city_rt --minutes 60 --max-cases 200 --outdir results/city_rt_figs


数据源：

SF311: San Francisco 311 Open Data Service

Open-Meteo: Weather & Air Quality API

输出：

results/city_rt_figs/throughput.png

results/city_rt_figs/latency_hist.png

results/city_rt_figs/cache_hit_ma.png

2. 自动驾驶（OSM Overpass + Open-Meteo）

命令：

PYTHONPATH=. python cli.py ad_rt --outdir results/ad_rt_figs


数据源：

Overpass API: OpenStreetMap road network

Open-Meteo: Weather

输出：

results/ad_rt_figs/throughput.png

results/ad_rt_figs/latency_hist.png

results/ad_rt_figs/cache_hit_ma.png

