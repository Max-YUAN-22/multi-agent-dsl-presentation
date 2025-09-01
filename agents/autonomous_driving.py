
from core.dsl import DSL, program

SYSTEM_PREFIX = (
    "You are a traffic incident agent. Policies: minimal JSON.\n"
    "Keys: kind, severity, edge, action.\n"
)

def _mk_prompt(scene:str) -> str:
    return SYSTEM_PREFIX + scene

@program
def driving_demo(dsl: DSL, *, ticks:int=50, p_collision:float=0.02, seed:int=7, llm_delay_ms:int=0, use_cache:bool=True):
    import random
    random.seed(seed)
    import time
    def _llm(p, role=None):
        if llm_delay_ms>0:
            time.sleep(llm_delay_ms/1000.0)
        return f"[{role}]OK:{p[-16:]}"
    dsl.use_llm(_llm, use_cache=use_cache)
    dsl.register("Perception", ["detect_incident"])
    dsl.register("TrafficManager", ["control"])
    dsl.register("Reroute", ["plan"])
    dsl.register("EMS", ["dispatch"])

    for t in range(ticks):
        if random.random() < p_collision:
            edge = f"E{random.randint(1,5)}-{random.randint(1,5)}"
            scene = f"Incident near {edge}. Vehicles stopped."
            det = dsl.gen("detect", prompt=_mk_prompt(scene), agent="Perception", regex=r".*")
            ctrl = dsl.delegate(det, "control", prompt=f"Close {edge} temporarily", agent="TrafficManager", regex=r".*")
            plan = dsl.delegate(det, "plan", prompt=f"Reroute around {edge}", agent="Reroute", regex=r".*")
            ems  = dsl.delegate(det, "dispatch", prompt=f"Dispatch tow to {edge}", agent="EMS", regex=r".*")
            dsl.join([det, ctrl, plan, ems])
    return {"done": True}
