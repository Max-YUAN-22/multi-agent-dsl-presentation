
import argparse, os
from experiments.smart_city import main as city_main
from experiments.autonomous_driving import main as ad_main
from experiments.city_realtime import main as city_rt_main
from experiments.ad_realtime import main as ad_rt_main

def run_city(args):
    res = city_main(ticks=args.ticks, p_fall=args.p_fall, p_low_moisture=args.p_moisture, seed=args.seed, outdir=args.outdir, with_cache=args.with_cache, llm_delay_ms=args.llm_delay_ms)
    print("[CITY] done:", res, "metrics->", os.path.abspath(args.outdir))

def run_ad(args):
    res = ad_main(ticks=args.ticks, p_collision=args.p_collision, seed=args.seed, outdir=args.outdir, with_cache=args.with_cache, llm_delay_ms=args.llm_delay_ms)
    print("[AD] done:", res, "metrics->", os.path.abspath(args.outdir))

def run_city_rt(args):
    res = city_rt_main(minutes=args.minutes, max_cases=args.max_cases, outdir=args.outdir)
    print("[CITY-RT] done:", res)

def run_ad_rt(args):
    res = ad_rt_main(outdir=args.outdir)
    print("[AD-RT] done:", res)

def main():
    parser = argparse.ArgumentParser("ma-run")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_city = sub.add_parser("city")
    p_city.add_argument("--ticks", type=int, default=60)
    p_city.add_argument("--p-fall", dest="p_fall", type=float, default=0.02)
    p_city.add_argument("--p-moisture", dest="p_moisture", type=float, default=0.03)
    p_city.add_argument("--seed", type=int, default=7)
    p_city.add_argument("--outdir", type=str, default="results/city")
    p_city.add_argument("--with-cache", type=lambda x: x.lower()=="true", default=True)
    p_city.add_argument("--llm-delay-ms", type=int, default=0)
    p_city.set_defaults(func=run_city)

    p_ad = sub.add_parser("ad")
    p_ad.add_argument("--ticks", type=int, default=50)
    p_ad.add_argument("--p-collision", dest="p_collision", type=float, default=0.02)
    p_ad.add_argument("--seed", type=int, default=7)
    p_ad.add_argument("--outdir", type=str, default="results/ad")
    p_ad.add_argument("--with-cache", type=lambda x: x.lower()=="true", default=True)
    p_ad.add_argument("--llm-delay-ms", type=int, default=0)
    p_ad.set_defaults(func=run_ad)
    
    # Real-time data demo
    p_city_rt = sub.add_parser("city_rt")
    p_city_rt.add_argument("--minutes", type=int, default=60)
    p_city_rt.add_argument("--max-cases", type=int, default=200)
    p_city_rt.add_argument("--outdir", type=str, default="results/city_rt_figs")
    p_city_rt.set_defaults(func=run_city_rt)

    p_ad_rt = sub.add_parser("ad_rt")
    p_ad_rt.add_argument("--outdir", type=str, default="results/ad_rt_figs")
    p_ad_rt.set_defaults(func=run_ad_rt)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
