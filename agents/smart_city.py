
from core.dsl import DSL, program

CITY_PREFIX = (
    "You are a city ops agent. Output minimal JSON.\n"
    "Keys: kind, severity, zone, action.\n"
)

def _mk_prompt(observation:str) -> str:
    return CITY_PREFIX + observation

@program
def city_demo(dsl: DSL, *, ticks:int=60, p_fall:float=0.02, p_low_moisture:float=0.03, seed:int=7, llm_delay_ms:int=0, use_cache:bool=True):
    import random
    random.seed(seed)
    import time
    def _llm(p, role=None):
        if llm_delay_ms>0:
            time.sleep(llm_delay_ms/1000.0)
        return f"[{role}]OK:{p[-16:]}"
    dsl.use_llm(_llm, use_cache=use_cache)
    dsl.register("PerceptionHuman", ["fall"])
    dsl.register("PerceptionEnv", ["env"])
    dsl.register("Scheduler", ["dispatch"])
    dsl.register("Sprinkler", ["irrigate"])
    dsl.register("EMS", ["ems"])
    for t in range(ticks):
        if random.random() < p_fall:
            zone = f"Z{random.randint(1,4)}"
            obs = f"Possible fall in {zone}"
            det = dsl.gen("fall", prompt=_mk_prompt(obs), agent="PerceptionHuman", regex=r".*")
            ems = dsl.delegate(det, "ems", prompt=f"Dispatch EMS to {zone}", agent="EMS", regex=r".*")
            dsl.join([det, ems])
        if random.random() < p_low_moisture:
            zone = f"Z{random.randint(1,4)}"
            obs = f"Soil moisture low at {zone}"
            det = dsl.gen("moist", prompt=_mk_prompt(obs), agent="PerceptionEnv", regex=r".*")
            irg = dsl.delegate(det, "irrigate", prompt=f"Irrigate {zone} for 5min", agent="Sprinkler", regex=r".*")
            dsl.join([det, irg])
    return {"done": True}
