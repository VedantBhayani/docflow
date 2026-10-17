"""Evaluation harness: run the pipeline on a split of the synthetic set and score it against truth.

    uv run python -m docflow.evaluate --split dev
    uv run python -m docflow.evaluate --split heldout --final     # the one reported run

Metric definitions match spec section 8. Fields are scored by value: amounts as numbers,
dates as dates, IDs and text whitespace/case-insensitively. Held-out runs are refused
without --final and every one is appended to results/heldout_runs.log.
"""

import argparse
import json
import re
import statistics
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from docflow.parse import parse_amount, parse_date, parse_rate
from docflow.pipeline import process_batch

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "synthetic" / "invoices"
RESULTS = ROOT / "results"
KEY_FIELDS = ["supplier_gstin", "recipient_gstin", "invoice_no", "invoice_date", "taxable_total", "grand_total"]
AMOUNTS = {"taxable_total", "cgst_total", "sgst_total", "igst_total", "round_off", "grand_total", "unit_price", "taxable_value", "cgst", "sgst", "igst", "qty"}
# Mistral Small 4 list price (USD per 1M tokens), docs.mistral.ai pricing, read 2026-10-16 (research note 03).
PRICE_IN, PRICE_OUT = 0.15, 0.60


def same_value(name: str, got: str | None, want: str | None) -> bool:
    base = name.split(".")[-1]
    if got is None or want is None:
        return got is None and want is None
    if base in AMOUNTS:
        a, b = parse_amount(got), parse_amount(want)
        return a is not None and a == b
    if base == "invoice_date":
        return parse_date(got) is not None and parse_date(got) == parse_date(want)
    if base == "gst_rate":
        return parse_rate(got) is not None and parse_rate(got) == parse_rate(want)
    return re.sub(r"\s+", "", got).casefold() == re.sub(r"\s+", "", want).casefold()


def score_document(result, truth: dict) -> dict:
    fields = []
    for name, want in truth["fields"].items():
        got = result.fields.get(name)
        fields.append({"name": name, "ok": same_value(name, got.text if got else None, want), "status": got.status if got else "ABSENT",
                       "got": got.text if got else None, "want": want})
    for name in ("irn",):  # printed only on QR documents; elsewhere the correct answer is "not printed"
        if name not in truth["fields"] and name in result.fields:
            got = result.fields[name]
            fields.append({"name": name, "ok": got.text is None, "status": got.status, "got": got.text, "want": None})
    for i, want_line in enumerate(truth["lines"]):
        got_line = result.lines[i] if i < len(result.lines) else {}
        for name, want in want_line.items():
            got = got_line.get(name)
            fields.append({"name": f"lines.{name}", "ok": same_value(name, got.text if got else None, want),
                           "status": got.status if got else "ABSENT", "got": got.text if got else None, "want": want})
    extra_lines = max(0, len(result.lines) - len(truth["lines"]))
    blocking = sorted({f.check_id for f in result.flags if f.severity == "BLOCKING"})
    expected, acceptable = set(truth["expected_flags"]), set(truth["acceptable_flags"])
    exact = set(blocking) == expected or (expected <= set(blocking) and set(blocking) - expected <= acceptable)
    if not exact and truth["defect"] == "rotated_page":
        exact = set(blocking) <= acceptable
    caught = bool(expected) and expected <= set(blocking)
    return {"fields": fields, "extra_lines": extra_lines, "blocking": blocking, "expected": sorted(expected),
            "flags_exact": exact, "caught": caught, "status": result.status,
            "qr_status": (result.qr or {}).get("status"), "llm": result.llm,
            "warnings": sorted({f.check_id for f in result.flags if f.severity == "WARNING"})}


def _pct(a: int, b: int) -> str:
    return f"{a}/{b} ({a / b:.1%})" if b else "n/a"


def summarise(rows: list[dict]) -> dict:
    m: dict = {}
    allf = [f for r in rows for f in r["score"]["fields"]]
    m["documents"] = len(rows)
    m["field_accuracy"] = (sum(f["ok"] for f in allf), len(allf))
    m["key_field_accuracy"] = (sum(f["ok"] for f in allf if f["name"] in KEY_FIELDS), sum(f["name"] in KEY_FIELDS for f in allf))
    for dim in ("scan", "template"):
        groups = defaultdict(list)
        for r in rows:
            groups[r["doc"][dim]].extend(r["score"]["fields"])
        m[f"field_accuracy_by_{dim}"] = {k: (sum(f["ok"] for f in v), len(v)) for k, v in sorted(groups.items())}
    per_field = defaultdict(list)
    for f in allf:
        per_field[f["name"]].append(f["ok"])
    m["field_accuracy_by_field"] = {k: (sum(v), len(v)) for k, v in sorted(per_field.items())}
    extracted = [f for f in allf if f["got"] is not None]
    m["grounding_rate"] = (sum(f["status"] in ("GROUNDED", "VERIFIED") for f in extracted), len(extracted))
    m["verified_key_fields"] = (sum(f["status"] == "VERIFIED" for f in allf if f["name"] in KEY_FIELDS), sum(f["name"] in KEY_FIELDS for f in allf))
    defects = [r for r in rows if r["doc"]["defect"] and r["score"]["expected"]]
    m["defect_recall"] = (sum(r["score"]["caught"] for r in defects), len(defects))
    m["defect_recall_by_type"] = {}
    for t in sorted({r["doc"]["defect"] for r in defects}):
        rs = [r for r in defects if r["doc"]["defect"] == t]
        m["defect_recall_by_type"][t] = (sum(r["score"]["caught"] for r in rs), len(rs))
    clean = [r for r in rows if not r["score"]["expected"] and r["doc"]["defect"] not in ("rotated_page",)]
    m["false_flag_rate"] = (sum(bool(r["score"]["blocking"]) for r in clean), len(clean))
    m["straight_through_rate"] = (sum(not r["score"]["blocking"] for r in clean), len(clean))
    m["flags_exactly_as_labelled"] = (sum(r["score"]["flags_exact"] for r in rows), len(rows))
    inj = [r for r in rows if r["doc"]["defect"] == "prompt_injection"]
    m["prompt_injection_unaffected"] = (sum(r["score"]["flags_exact"] and all(f["ok"] for f in r["score"]["fields"] if f["name"] in KEY_FIELDS) for r in inj), len(inj))
    qr_docs = [r for r in rows if r["doc"]["qr"]]
    by_scan = defaultdict(list)
    for r in qr_docs:
        by_scan[r["doc"]["scan"]].append(r["score"]["qr_status"] != "NO_QR")
    m["qr_read_rate_by_scan"] = {k: (sum(v), len(v)) for k, v in sorted(by_scan.items())}
    tokens_in = [r["score"]["llm"].get("prompt_tokens") or 0 for r in rows]
    tokens_out = [r["score"]["llm"].get("completion_tokens") or 0 for r in rows]
    usd = [(i * PRICE_IN + o * PRICE_OUT) / 1e6 for i, o in zip(tokens_in, tokens_out)]
    m["llm_usd_per_doc_mean"] = round(statistics.mean(usd), 6) if usd else None
    m["llm_tokens_per_doc_mean"] = (round(statistics.mean(tokens_in)), round(statistics.mean(tokens_out))) if rows else None
    fresh = [r["seconds"] for r in rows if not r["score"]["llm"].get("cache_hit")]
    m["latency_uncached_seconds"] = ({"n": len(fresh), "p50": round(statistics.median(fresh), 2), "p95": round(sorted(fresh)[max(0, int(len(fresh) * 0.95) - 1)], 2)}
                                     if fresh else "n/a: every LLM call came from cache, so timings would not be real")
    return m


def report_markdown(split: str, m: dict, rows: list[dict], final: bool) -> str:
    lines = [f"# DocFlow evaluation: {split} split{' (FINAL held-out run)' if final else ''}", "",
             f"Run at {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC, {m['documents']} documents, trust store `test`.", "",
             "| Metric | Result |", "|---|---|"]
    for key, label in [("field_accuracy", "Field accuracy (all fields, by value)"), ("key_field_accuracy", "Key-field accuracy"),
                       ("grounding_rate", "Grounding rate (extracted values proven on the page)"), ("verified_key_fields", "Key fields VERIFIED by an independent source"),
                       ("defect_recall", "Defect recall (injected defects caught)"), ("false_flag_rate", "False-flag rate (clean docs with a blocking flag)"),
                       ("straight_through_rate", "Straight-through rate (clean docs, no blocking flag)"),
                       ("flags_exactly_as_labelled", "Documents flagged exactly as labelled"), ("prompt_injection_unaffected", "Prompt-injection docs unaffected")]:
        a, b = m[key]
        lines.append(f"| {label} | {_pct(a, b)} |")
    lines.append(f"| LLM cost per document (mean) | ${m['llm_usd_per_doc_mean']} |")
    lines.append(f"| Latency per document, uncached | {m['latency_uncached_seconds']} |")
    for title, key in [("By scan level", "field_accuracy_by_scan"), ("By template", "field_accuracy_by_template"),
                       ("Defect recall by type", "defect_recall_by_type"), ("QR read rate by scan level", "qr_read_rate_by_scan"),
                       ("By field", "field_accuracy_by_field")]:
        lines += ["", f"## {title}", "", "| | Result |", "|---|---|"] + [f"| {k} | {_pct(*v)} |" for k, v in m[key].items()]
    misses = [(r["doc"]["id"], f) for r in rows for f in r["score"]["fields"] if not f["ok"]]
    lines += ["", "## Every field error", "", "| Doc | Field | Got | Truth | Status |", "|---|---|---|---|---|"]
    lines += [f"| {d} | {f['name']} | `{f['got']}` | `{f['want']}` | {f['status']} |" for d, f in misses] or ["| none | | | | |"]
    wrong = [r for r in rows if not r["score"]["flags_exact"]]
    lines += ["", "## Every flag outcome that differs from its label", "", "| Doc | Scan | Defect | Blocking flags | Expected |", "|---|---|---|---|---|"]
    lines += [f"| {r['doc']['id']} | {r['doc']['scan']} | {r['doc']['defect'] or '-'} | {', '.join(r['score']['blocking']) or '-'} | {', '.join(r['score']['expected']) or '-'} |" for r in wrong] or ["| none | | | | |"]
    return "\n".join(lines) + "\n"


def run(split: str, final: bool = False) -> dict:
    if split == "heldout" and not final:
        raise SystemExit("Held-out is the reported run: pass --final, and run it once.")
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))["documents"]
    docs = [d for d in manifest if d["split"] == split]
    t0 = time.time()
    results = process_batch([DATA / f"{d['id']}.pdf" for d in docs], trust="test")
    rows = []
    for d, r in zip(docs, results):
        truth = json.loads((DATA / f"{d['id']}.truth.json").read_text(encoding="utf-8"))
        rows.append({"doc": d, "seconds": r.seconds, "score": score_document(r, truth)})
    m = summarise(rows)
    m["wall_seconds"] = round(time.time() - t0, 1)
    out = RESULTS / f"{datetime.now():%Y-%m-%d}" / split
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(m, indent=2, default=str), encoding="utf-8")
    (out / "report.md").write_text(report_markdown(split, m, rows, final), encoding="utf-8")
    with (out / "per_doc.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, default=str) + "\n")
    if split == "heldout":
        with (RESULTS / "heldout_runs.log").open("a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} final held-out run -> {out}\n")
    return m


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m docflow.evaluate")
    parser.add_argument("--split", choices=["dev", "heldout"], default="dev")
    parser.add_argument("--final", action="store_true", help="required for the held-out run")
    args = parser.parse_args()
    m = run(args.split, args.final)
    for k in ("field_accuracy", "key_field_accuracy", "grounding_rate", "defect_recall", "false_flag_rate", "flags_exactly_as_labelled"):
        print(f"{k:28} {_pct(*m[k])}")
    print(f"{'qr_read_rate_by_scan':28} {m['qr_read_rate_by_scan']}")


if __name__ == "__main__":
    main()
