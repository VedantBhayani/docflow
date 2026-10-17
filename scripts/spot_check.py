"""Real-world spot check: run DocFlow on your own documents and record outcomes only.

    Put PDFs in spot_check/invoices/ and spot_check/statements/ (both gitignored), then:
    uv run python scripts/spot_check.py

Writes spot_check/outcomes.md: one row per document with its status, the checks that fired and
how many fields were grounded. No document text and no extracted values are written, so the
file can be summarised in the README without exposing anything confidential.
"""

from collections import Counter
from pathlib import Path

from docflow.pipeline import process

ROOT = Path(__file__).resolve().parents[1] / "spot_check"


def main() -> None:
    rows = []
    for kind, folder in (("invoice", "invoices"), ("statement", "statements")):
        for i, pdf in enumerate(sorted((ROOT / folder).glob("*.pdf")), 1):
            label = f"{kind} {i}"  # never the file name: names can identify a client
            try:
                r = process(pdf, kind=kind)
            except Exception as exc:
                rows.append((label, "ERROR", type(exc).__name__, "", ""))
                print(f"{label}: ERROR {type(exc).__name__}")
                continue
            cells = list(r.fields.values()) + [f for line in r.lines for f in line.values()]
            status = Counter(str(f.status) for f in cells if f.text)
            blocking = sorted({f.check_id for f in r.flags if f.severity == "BLOCKING"})
            warnings = sorted({f.check_id for f in r.flags if f.severity == "WARNING"})
            grounded = status["VERIFIED"] + status["GROUNDED"]
            rows.append((label, str(r.status), ", ".join(blocking) or "-", ", ".join(warnings) or "-",
                         f"{grounded}/{sum(status.values())} ({'+'.join(sorted(set(r.page_sources)))})"))
            print(f"{label}: {r.status} blocking={blocking} warnings={warnings}")
            for f in r.flags:  # printed to your screen only, so you can judge each flag: right or wrong?
                print(f"    {f.severity:8} {f.check_id}: {f.message}")
    out = ["| Document | Status | Blocking checks | Warnings | Values grounded (pages) | Flag correct? (fill in) |", "|---|---|---|---|---|---|"]
    out += [f"| {a} | {b} | {c} | {d} | {e} | |" for a, b, c, d, e in rows]
    (ROOT / "outcomes.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"\nWrote {ROOT / 'outcomes.md'}")


if __name__ == "__main__":
    for sub in ("invoices", "statements"):
        (ROOT / sub).mkdir(parents=True, exist_ok=True)
    main()
