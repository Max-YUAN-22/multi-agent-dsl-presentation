
import argparse, os
from experiments.smart_city import main as city_main
from experiments.autonomous_driving import main as ad_main

def run_city(args):
    res = city_main(ticks=args.ticks, p_fall=args.p_fall, p_low_moisture=args.p_moisture, seed=args.seed, outdir=args.outdir, with_cache=args.with_cache, llm_delay_ms=args.llm_delay_ms)
    print("[CITY] done:", res, "metrics->", os.path.abspath(args.outdir))

def run_ad(args):
    res = ad_main(ticks=args.ticks, p_collision=args.p_collision, seed=args.seed, outdir=args.outdir, with_cache=args.with_cache, llm_delay_ms=args.llm_delay_ms)
    print("[AD] done:", res, "metrics->", os.path.abspath(args.outdir))

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

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
