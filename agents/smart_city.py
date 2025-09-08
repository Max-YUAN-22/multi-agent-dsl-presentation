
from dsl.dsl import DSL, program
from agents.perception_human_agent import PerceptionHumanAgent
from agents.perception_env_agent import PerceptionEnvAgent
from agents.sprinkler_agent import SprinklerAgent
from agents.ems_agent import EMSAgent
from agents.traffic_incident_agent import TrafficIncidentAgent

class SmartCity:
    def __init__(self, dsl: DSL, llm_delay_ms: int = 0, use_cache: bool = True):
        self.dsl = dsl
        self.llm_delay_ms = llm_delay_ms
        self.use_cache = use_cache
        self._setup_llm()
        self._setup_agents()

    def _setup_llm(self):
        import time
        def _llm(p, role=None):
            if self.llm_delay_ms > 0:
                time.sleep(self.llm_delay_ms / 1000.0)
            return f"[{role}]OK:{p[-16:]}"
        self.dsl.use_llm(_llm, use_cache=self.use_cache)

    def _setup_agents(self):
        self.perception_human_agent = PerceptionHumanAgent(self.dsl)
        self.perception_env_agent = PerceptionEnvAgent(self.dsl)
        self.sprinkler_agent = SprinklerAgent(self.dsl)
        self.ems_agent = EMSAgent(self.dsl)
        self.traffic_incident_agent = TrafficIncidentAgent(self.dsl)

    def _mk_prompt(self, observation: str) -> str:
        return (
            "You are a city ops agent. Output minimal JSON.\n"
            "Keys: kind, severity, zone, action.\n"
            f"{observation}"
        )

    def handle_fall(self, zone: str):
        obs = f"Possible fall in {zone}"
        det = self.dsl.gen("fall", prompt=self._mk_prompt(obs), agent=self.perception_human_agent).with_regex(r".*").schedule()
        ems = self.dsl.gen("ems", prompt=f"Dispatch EMS to {zone}", agent=self.ems_agent).with_regex(r".*").schedule()
        return [det, ems]

    def handle_low_moisture(self, zone: str):
        obs = f"Soil moisture low at {zone}"
        det = self.dsl.gen("moist", prompt=self._mk_prompt(obs), agent=self.perception_env_agent).with_regex(r".*").schedule()
        irg = self.dsl.gen("irrigate", prompt=f"Irrigate {zone} for 5min", agent=self.sprinkler_agent).with_regex(r".*").schedule()
        return [det, irg]

    def handle_traffic_incident(self, zone: str):
        obs = f"Traffic incident in {zone}"
        det = self.dsl.gen("traffic_incident", prompt=self._mk_prompt(obs), agent=self.traffic_incident_agent).with_regex(r".*").schedule()
        return [det]

@program
def city_demo(dsl: DSL, *, ticks:int=60, p_fall:float=0.02, p_low_moisture:float=0.03, p_traffic_incident:float=0.01, seed:int=7, llm_delay_ms:int=0, use_cache:bool=True, outdir: str | None = None):
    import random
    random.seed(seed)

    city = SmartCity(dsl, llm_delay_ms=llm_delay_ms, use_cache=use_cache)
    all_tasks = []

    for t in range(ticks):
        if random.random() < p_fall:
            zone = f"Z{random.randint(1, 4)}"
            all_tasks.extend(city.handle_fall(zone))
        if random.random() < p_low_moisture:
            zone = f"Z{random.randint(1, 4)}"
            all_tasks.extend(city.handle_low_moisture(zone))
        if random.random() < p_traffic_incident:
            zone = f"Z{random.randint(1, 4)}"
            all_tasks.extend(city.handle_traffic_incident(zone))
    
    summary = dsl.join(all_tasks)
    if outdir:
        dsl.metrics.write_csv(outdir)
    
    return {"done": True, "summary": summary}
