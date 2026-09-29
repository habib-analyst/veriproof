"""EviForge-DB build entry point.

Usage:
    python data_build.py --out data/processed/eviforge-db-v1 \
        --n-real 2000 --n-tampered 2000 --seed 20260929
    python data_build.py ... --hf   # additionally export a Hugging Face dataset
"""
import argparse
import json
from pathlib import Path

from veriproof.data.dataset import build_hf_dataset, compute_stats, generate_samples


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="data_build", description="Build EviForge-DB")
    parser.add_argument("--out", required=True)
    parser.add_argument("--n-real", type=int, default=2000)
    parser.add_argument("--n-tampered", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260929)
    parser.add_argument("--hf", action="store_true", help="also export an HF dataset")
    args = parser.parse_args(argv)

    samples = generate_samples(args.n_real, args.n_tampered, args.seed)
    stats = compute_stats(samples)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))

    for s in samples:
        s["image"].save(out / f"img_{s['label']}_{s['seed']}_{s['tamper_op']}.png")

    if args.hf:
        build_hf_dataset(str(out / "hf"), args.n_real, args.n_tampered, args.seed)
        print(f"HF dataset written to {out / 'hf'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
