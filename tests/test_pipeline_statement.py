"""Statement tracer: two-page statement (with a carry-forward row) and a broken-chain twin,
end to end against truth, and the Statement Line contract that Recon consumes."""

import csv
import json
from pathlib import Path

import pytest

from docflow.pipeline import process, statement_lines, write_statement_lines

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic" / "statement_tracer"
CONTRACT = ["statement_id", "bank_hint", "account_last4", "line_no", "txn_date", "value_date", "narration_raw", "channel", "ref_no",
            "bank_ref", "cheque_no", "counterparty_hint", "amount", "direction", "balance", "page", "bbox", "field_status", "flag_ids"]


def _run(stem):
    try:
        r = process(DATA / f"{stem}.pdf", kind="statement")
    except RuntimeError as exc:
        if "MISTRAL_API_KEY" in str(exc):
            pytest.skip("no cached response and no API key")
        raise
    return r, json.loads((DATA / f"{stem}.truth.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def clean():
    return _run("stmt-tracer-01")


@pytest.fixture(scope="module")
def broken():
    return _run("stmt-tracer-02-broken")


def test_clean_statement_is_clean_and_complete(clean):
    r, t = clean
    assert r.status == "CLEAN" and len(r.lines) == len(t["lines"])
    assert r.fields["opening_balance"].text == t["fields"]["opening_balance"]  # summary box, not the page-2 B/F row
    assert r.fields["closing_balance"].text == t["fields"]["closing_balance"]


def test_statement_lines_match_truth_exactly(clean):
    r, t = clean
    rows = statement_lines(r)
    assert [list(row) for row in rows[:1]] == [CONTRACT]
    for row, d in zip(rows, t["derived"]):
        assert (row["channel"], row["ref_no"], row["direction"], row["amount"], row["cheque_no"]) == \
               (d["channel"], d["ref_no"], d["direction"], d["amount"], d["cheque_no"])
        assert row["amount"] is None or "," not in row["amount"]  # decimal string, never grouped or float


def test_broken_chain_is_s1_on_the_broken_row_and_carry_forward_is_not_flagged(broken):
    r, t = broken
    s1 = [f.fields[0] for f in r.flags if f.check_id == "S1"]
    assert s1[0] == f"lines.{t['broken_line']}.balance"
    assert {f.check_id for f in r.flags if f.severity == "BLOCKING"} == {"S1"}


def test_contract_is_written_as_jsonl_and_csv(clean, tmp_path):
    r, _ = clean
    write_statement_lines(r, tmp_path / "lines.jsonl")
    write_statement_lines(r, tmp_path / "lines.csv")
    rows = [json.loads(x) for x in (tmp_path / "lines.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(rows) == len(r.lines) and list(rows[0]) == CONTRACT
    with (tmp_path / "lines.csv").open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames == CONTRACT and len(list(reader)) == len(r.lines)
