"""python -m docflow.synth invoices --seed 7 [--out data/synthetic/invoices]"""

import argparse
from collections import Counter
from pathlib import Path

from docflow.synth.invoice import generate_invoice_set

ROOT = Path(__file__).resolve().parents[3]


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m docflow.synth")
    parser.add_argument("what", choices=["invoices"])
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "synthetic" / "invoices")
    args = parser.parse_args()
    manifest = generate_invoice_set(args.out, seed=args.seed)
    print(f"{len(manifest)} invoices -> {args.out}")
    print("splits:", dict(Counter(m["split"] for m in manifest)), "| defects:", dict(Counter(m["defect"] for m in manifest if m["defect"])))


if __name__ == "__main__":
    main()
