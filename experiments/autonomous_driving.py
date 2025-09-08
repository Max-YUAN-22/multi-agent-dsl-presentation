# experiments/autonomous_driving.py
from dsl.dsl import DSL
from agents.autonomous_driving import driving_demo
from integrations.spark_x1 import get_llm_with_fallback

def main(ticks: int = 50, p_collision: float = 0.02, seed: int = 7, outdir:str|None=None, with_cache:bool=True, llm_delay_ms:int=0):
    # 并发可按配额调大：workers=20（与你 Spark 并发上限一致）
    dsl = DSL(workers=20)
    dsl.use_llm(get_llm_with_fallback())
    res = driving_demo(dsl, ticks=ticks, p_collision=p_collision, seed=seed, outdir=outdir, use_cache=with_cache, llm_delay_ms=llm_delay_ms)
    return res

if __name__ == "__main__":
    print(main())
