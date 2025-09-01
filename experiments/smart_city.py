
from core.dsl import DSL
from agents.smart_city import city_demo
import os, subprocess, sys

def main(ticks:int=60, p_fall:float=0.02, p_low_moisture:float=0.03, seed:int=7, outdir: str = 'results/city', with_cache: bool = True, llm_delay_ms: int = 0):
    dsl = DSL()
    res = city_demo(dsl, ticks=ticks, p_fall=p_fall, p_low_moisture=p_low_moisture, seed=seed, llm_delay_ms=llm_delay_ms, use_cache=with_cache)
    dsl.metrics.write_csv(outdir)
    events_csv = os.path.join(outdir, 'events.csv')
    plotter = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'plot_metrics.py')
    subprocess.run([sys.executable, plotter, '--events', events_csv, '--outdir', outdir], check=True)
    return res

if __name__ == "__main__":
    print(main())
