
from core.dsl import DSL
from agents.autonomous_driving import driving_demo
import os, subprocess, sys

def main(ticks: int = 50, p_collision: float = 0.02, seed: int = 7, outdir: str = 'results/ad', with_cache: bool = True, llm_delay_ms: int = 0):
    dsl = DSL()
    res = driving_demo(dsl, ticks=ticks, p_collision=p_collision, seed=seed, llm_delay_ms=llm_delay_ms, use_cache=with_cache)
    dsl.metrics.write_csv(outdir)
    events_csv = os.path.join(outdir, 'events.csv')
    plotter = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'plot_metrics.py')
    subprocess.run([sys.executable, plotter, '--events', events_csv, '--outdir', outdir], check=True)
    return res

if __name__ == "__main__":
    print(main())
