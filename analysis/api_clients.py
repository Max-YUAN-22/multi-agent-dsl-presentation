# analysis/api_clients.py
from __future__ import annotations
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import requests

# ---------- Utilities ----------
def _iso_utc_ms(dt: datetime) -> str:
    """Formats a datetime object to an ISO 8601 string with milliseconds."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000")

# ---------- Overpass ----------
class OverpassClient:
    """
    A minimalist client for fetching data from the OpenStreetMap Overpass API.
    """
    BASE = "https://overpass-api.de/api/interpreter"

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()

    def fetch_roads(self, bbox: str) -> Dict[str, Any]:
        """
        Fetches all roads within a given bounding box.
        bbox: "south,west,north,east"
        """
        query = f"""
        [out:json][timeout:25];
        (
          way["highway"]({bbox});
        );
        out body;
        >;
        out skel qt;
        """
        r = self.session.post(self.BASE, data=query, timeout=30)
        r.raise_for_status()
        return r.json()

# ---------- SF311 ----------
# Case Data from San Francisco 311 (SF311): vw6y-z8j6
SF311_DATASET = "vw6y-z8j6"
SF311_BASE = f"https://data.sfgov.org/resource/{SF311_DATASET}.json"

class SF311Client:
    """SF311 SODA client: Uses millisecond timestamps and filters by >=start, with $order/$limit."""
    def __init__(self, app_token: Optional[str] = None, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.app_token = app_token or os.getenv("SOCRATA_APP_TOKEN")
        if self.app_token:
            self.session.headers.update({"X-App-Token": self.app_token})

    def fetch_recent_cases(self, minutes: int = 20, limit: int = 200) -> List[Dict[str, Any]]:
        # Avoid future timestamps by leaving a 2-minute buffer
        end = datetime.now(timezone.utc) - timedelta(minutes=2)
        start = end - timedelta(minutes=max(1, minutes))
        # Robust approach: filter by >= start, order by requested_datetime DESC, and take the top N
        params = {
            "$where": f"requested_datetime >= '{_iso_utc_ms(start)}'",
            "$order": "requested_datetime DESC",
            "$limit": min(max(1, limit), 1000),
        }
        r = self.session.get(SF311_BASE, params=params, timeout=25)
        r.raise_for_status()
        return r.json() or []

# ---------- NYC 311 ----------
# 311 Service Requests from 2010 to Present: erm2-nwe9
NYC311_DATASET = "erm2-nwe9"
NYC311_BASE = f"https://data.cityofnewyork.us/resource/{NYC311_DATASET}.json"

class NYC311Client:
    """NYC 311: Also uses millisecond timestamps and filters by >= start."""
    def __init__(self, app_token: Optional[str] = None, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.app_token = app_token or os.getenv("SOCRATA_APP_TOKEN")
        if self.app_token:
            self.session.headers.update({"X-App-Token": self.app_token})

    def fetch_recent_cases(self, minutes: int = 20, limit: int = 200) -> List[Dict[str, Any]]:
        end = datetime.now(timezone.utc) - timedelta(minutes=2)
        start = end - timedelta(minutes=max(1, minutes))
        params = {
            "$where": f"created_date >= '{_iso_utc_ms(start)}'",
            "$order": "created_date DESC",
            "$limit": min(max(1, limit), 1000),
        }
        r = self.session.get(NYC311_BASE, params=params, timeout=25)
        r.raise_for_status()
        return r.json() or []

# ---------- Open-Meteo (kept for unified dependency management) ----------
class OpenMeteoClient:
    BASE = "https://api.open-meteo.com/v1/forecast"
    AQ_BASE = "https://air-quality-api.open-meteo.com/v1/air-quality"

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()

    def fetch_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        params = {"latitude": lat, "longitude": lon, "hourly": "precipitation", "past_days": 1}
        r = self.session.get(self.BASE, params=params, timeout=15)
        r.raise_for_status()
        return r.json()

    def fetch_air_quality(self, lat: float, lon: float) -> Dict[str, Any]:
        params = {"latitude": lat, "longitude": lon, "hourly": "pm2_5"}
        r = self.session.get(self.AQ_BASE, params=params, timeout=15)
        r.raise_for_status()
        return r.json()
