"""Label integrity for the statement evaluation set (same standard as the invoice set)."""

import json
import re
from collections import Counter

import pymupdf
import pytest

from docflow.checks_statement import run_statement_checks
from docflow.models import Field, FieldStatus, Severity
from docflow.narration import classify, extract_cheque, extract_reference
from docflow.evaluate import same_value
from docflow.ingest import load
from docflow.statement_table import parse_tables
from docflow.synth.statement import LAYOUTS, SIDED, STATEMENT_DEFECTS, generate_statement_set


@pytest.fixture(scope="module")
def stmts(tmp_path_factory):
    out = tmp_path_factory.mktemp("statements")
    manifest = generate_statement_set(out, seed=11)
    return out, manifest, {m["id"]: json.loads((out / f"{m['id']}.truth.json").read_text(encoding="utf-8")) for m in manifest}


def _fields(t):
    fs = {k: Field(k, v, FieldStatus.GROUNDED) for k, v in t["fields"].items()}
    ls = [{k: Field(f"lines.{i}.{k}", v, FieldStatus.GROUNDED if v is not None else FieldStatus.MISSING) for k, v in ln.items()}
          for i, ln in enumerate(t["lines"])]
    return fs, ls


def test_composition(stmts):
    _, m, _ = stmts
    assert len(m) == 30
    assert Counter(d["template"] for d in m) == {lay: 5 for lay in LAYOUTS}
    assert Counter(d["scan"] for d in m) == {"digital": 20, "light": 5, "heavy": 5}
    assert Counter(d["defect"] for d in m if d["defect"]) == {d: 3 for d in STATEMENT_DEFECTS}
    for d in STATEMENT_DEFECTS:
        assert {x["split"] for x in m if x["defect"] == d} == {"dev", "heldout"}
    assert max(d["pages"] for d in m) == 6


def test_every_layout_has_defects_scans_and_a_clean_digital_statement(stmts):
    _, m, _ = stmts
    for lay in LAYOUTS:
        docs = [d for d in m if d["template"] == lay]
        assert sum(1 for d in docs if d["defect"]) == 2, lay
        assert any(d["scan"] != "digital" for d in docs), lay
        assert any(d["scan"] == "digital" and not d["defect"] for d in docs), lay
    assert not any(d["template"] in SIDED and d["defect"] == "both_dr_cr" for d in m)


def test_table_parser_reads_every_digital_dev_statement_exactly(stmts):
    out, m, truths = stmts
    for d in m:
        if d["scan"] != "digital" or d["split"] != "dev":
            continue
        t = truths[d["id"]]
        res = parse_tables(load(out / f"{d['id']}.pdf"))
        assert len(res.lines) == len(t["lines"]), d["id"]
        for i, (got, want) in enumerate(zip(res.lines, t["lines"])):
            for k, v in want.items():
                assert same_value(f"lines.{i}.{k}", got[k].text, v), (d["id"], i, k, got[k].text, v)


def test_overdraft_layout_prints_sided_balances_and_stress_events(stmts):
    _, m, truths = stmts
    t = truths[next(d["id"] for d in m if d["template"] == "signed")]
    assert any(ln["balance"].endswith(" Dr") for ln in t["lines"]) or t["fields"]["opening_balance"].endswith(" Dr")
    narr = [ln["narration"] for ln in t["lines"]]
    assert any(n.startswith("CHQ RET") for n in narr) and any(n.startswith("GST @18%") for n in narr)


def test_checks_on_truth_give_exactly_the_expected_flags(stmts):
    _, m, truths = stmts
    for d in m:
        blocking = {f.check_id for f in run_statement_checks(*_fields(truths[d["id"]])) if f.severity == Severity.BLOCKING}
        assert blocking == set(d["expected_flags"]), (d["id"], d["defect"], blocking)


def test_truth_references_are_recoverable_from_the_truth_narration(stmts):
    _, m, truths = stmts
    for d in m:
        t = truths[d["id"]]
        for ln, der in zip(t["lines"], t["derived"]):
            ch = classify(ln["narration"])
            assert ch == der["channel"], (d["id"], ln["narration"])
            assert extract_reference(ln["narration"], ch) == der["ref_no"], (d["id"], ln["narration"])
            if ch == "CHEQUE":
                assert (ln.get("ref_col") or extract_cheque(ln["narration"])) == der["cheque_no"], (d["id"], ln)


def test_every_truth_value_is_printed_on_digital_statements(stmts):
    out, m, truths = stmts
    for d in m:
        if d["scan"] != "digital":
            continue
        text = re.sub(r"\s+", "", "".join(p.get_text() for p in pymupdf.open(out / f"{d['id']}.pdf")))
        t = truths[d["id"]]
        for v in [v for v in t["fields"].values() if v] + [v for ln in t["lines"] for k, v in ln.items() if v and k != "narration"]:
            assert re.sub(r"\s+", "", v) in text, (d["id"], v)
        # Wrapped narrations are interleaved with other columns in PDF text order, so check them piece by piece.
        for ln in t["lines"]:
            for piece in re.split(r"[-/*\s]+", ln["narration"]):
                assert piece in text, (d["id"], ln["narration"], piece)
