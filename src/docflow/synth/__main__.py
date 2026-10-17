"""python -m docflow.synth invoices|statements [--seed N] [--out DIR]"""

import argparse
import shutil
from collections import Counter
from pathlib import Path

from docflow.synth.invoice import generate_invoice_set
from docflow.synth.statement import generate_statement_set

ROOT = Path(__file__).resolve().parents[3]
DEFAULTS = {"invoices": (7, "invoices"), "statements": (11, "statements")}


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m docflow.synth")
    parser.add_argument("what", choices=sorted(DEFAULTS))
    parser.add_argument("--seed", type=int)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    seed = args.seed if args.seed is not None else DEFAULTS[args.what][0]
    out = args.out or ROOT / "data" / "synthetic" / DEFAULTS[args.what][1]
    if args.what == "invoices":
        manifest = generate_invoice_set(out, seed=seed)
    else:
        if out.exists():
            shutil.rmtree(out)  # a regenerated set must not keep documents from an older composition
        manifest = generate_statement_set(out, seed=seed)
    print(f"{len(manifest)} {args.what} -> {out}")
    print("splits:", dict(Counter(m["split"] for m in manifest)), "| defects:", dict(Counter(m["defect"] for m in manifest if m["defect"])))


if __name__ == "__main__":
    main()
