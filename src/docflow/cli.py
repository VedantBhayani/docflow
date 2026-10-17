import argparse
import json
import sys

from docflow.pipeline import process


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="docflow")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("process", help="Extract, ground and check one Source Document; print the DocResult as JSON")
    p.add_argument("pdf")
    p.add_argument("--kind", default="invoice", choices=["invoice"])
    args = parser.parse_args(argv)

    if args.cmd == "process":
        result = process(args.pdf, kind=args.kind)
        sys.stdout.write(json.dumps(result.to_dict(), indent=2, default=str) + "\n")
        return 0 if result.status == "CLEAN" else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
