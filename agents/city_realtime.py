from __future__ import annotations
from dsl.dsl import DSL, program
from analysis.api_clients import SF311Client, OpenMeteoClient
from agents.perception311_agent import Perception311Agent
from agents.sanitation_agent import SanitationAgent
from agents.ems_agent import EMSAgent
from agents.enforcement_agent import EnforcementAgent

SF_LAT, SF_LON = 37.7749, -122.4194  # San Francisco

CITY_PREFIX = (
    "You are a city ops agent. Output minimal JSON with keys: kind, severity, zone, action.\n"
)

def _mk_prompt(obs: str) -> str:
    return CITY_PREFIX + obs

@program
def city_realtime(dsl: DSL, *, minutes: int = 60, max_cases: int = 200, outdir: str | None = None):
    """
    Real SF311 + Open-Meteo demo (no API keys). Produces tasks per 311 case and
    routes to different city agents based on category keywords.
    """
    dsl.use_llm(lambda p, role=None: f"[{role}]OK:{p[-40:]}")

    # Instantiate agents
    perception_agent = Perception311Agent(dsl)
    sanitation_agent = SanitationAgent(dsl)
    ems_agent = EMSAgent(dsl)
    enforcement_agent = EnforcementAgent(dsl)

    # Fetch real data
    sf = SF311Client()
    om = OpenMeteoClient()
    cases = sf.fetch_recent_cases(minutes=minutes*24*5, limit=max_cases)

    # Weather/air quality (for simple risk warnings, does not affect main logic)
    wx = om.fetch_weather(SF_LAT, SF_LON)
    aq = om.fetch_air_quality(SF_LAT, SF_LON)
    try:
        rain = float(wx["hourly"]["precipitation"][-1])
    except Exception:
        rain = 0.0
    try:
        pm25 = float(aq["hourly"]["pm2_5"][-1])
    except Exception:
        pm25 = 10.0

    # Convert 311 event stream into agent tasks
    all_tasks = []
    for c in cases:
        category = (c.get("service_subtype") or c.get("service_type") or c.get("service_name") or "unknown").lower()
        location = c.get("neighborhoods_sffind_boundaries") or c.get("neighborhood") or c.get("address") or "Unknown"
        obs = f"311 '{category}' at {location}"
        det = dsl.gen("e311", prompt=_mk_prompt(obs), agent=perception_agent).with_regex(r".*").schedule()

        if any(k in category for k in ["clean", "trash", "encamp", "litter"]):
            act = dsl.gen("clean", prompt=f"Dispatch sanitation to {location}", agent=sanitation_agent).with_regex(r".*").schedule()
        elif any(k in category for k in ["noise", "vehicle", "blocked", "parking"]):
            act = dsl.gen("law", prompt=f"Dispatch enforcement to {location}", agent=enforcement_agent).with_regex(r".*").schedule()
        else:
            act = dsl.gen("ems", prompt=f"Evaluate EMS need at {location}", agent=ems_agent).with_regex(r".*").schedule()
        
        all_tasks.extend([det, act])

    dsl.join(all_tasks)

    summary = {"done": True, "count": len(cases), "rain": rain, "pm25": pm25}
    if outdir:
        dsl.metrics.write_csv(outdir)
    return summary
