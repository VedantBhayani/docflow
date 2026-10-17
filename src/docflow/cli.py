import argparse
import json
import sys
from pathlib import Path

from docflow.checks import catalogue_markdown
from docflow.pipeline import process, process_batch

NL = "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="docflow")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("process", help="Extract, ground and check one Source Document; print the DocResult as JSON")
    p.add_argument("pdf")
    p.add_argument("--kind", default="invoice", choices=["invoice"])
    b = sub.add_parser("batch", help="Process every PDF in a folder (adds batch Checks such as A3 duplicates); print a summary")
    b.add_argument("folder")
    b.add_argument("--kind", default="invoice", choices=["invoice"])
    b.add_argument("--out", help="write all DocResults as JSON lines to this file")
    c = sub.add_parser("checks", help="Print the Check catalogue")
    c.add_argument("--markdown", action="store_true")
    args = parser.parse_args(argv)

    if args.cmd == "process":
        result = process(args.pdf, kind=args.kind)
        sys.stdout.write(json.dumps(result.to_dict(), indent=2, default=str) + NL)
        return 0 if result.status == "CLEAN" else 1
    if args.cmd == "batch":
        results = process_batch(sorted(Path(args.folder).glob("*.pdf")), kind=args.kind)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                for r in results:
                    fh.write(json.dumps(r.to_dict(), default=str) + NL)
        for r in results:
            ids = ",".join(sorted({f.check_id for f in r.flags})) or "-"
            sys.stdout.write(f"{r.status:8} {Path(r.path).name:40} {ids}{NL}")
        clean = sum(r.status == "CLEAN" for r in results)
        sys.stdout.write(f"{len(results)} documents: {clean} clean, {len(results) - clean} flagged{NL}")
        return 0
    if args.cmd == "checks":
        sys.stdout.write(catalogue_markdown() + NL)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
