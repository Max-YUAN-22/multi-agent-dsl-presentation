# experiments/smart_city.py
from dsl.dsl import DSL
from agents.smart_city import city_demo
from integrations.spark_x1 import get_llm_with_fallback

def main(ticks:int=60, p_fall:float=0.02, p_low_moisture:float=0.03, seed:int=7, outdir:str|None=None, with_cache:bool=True, llm_delay_ms:int=0):
    dsl = DSL(workers=20)
    dsl.use_llm(get_llm_with_fallback())
    res = city_demo(dsl, ticks=ticks, p_fall=p_fall, p_low_moisture=p_low_moisture, seed=seed, outdir=outdir, use_cache=with_cache, llm_delay_ms=llm_delay_ms)
    return res

if __name__ == "__main__":
    print(main())
