import json
from pathlib import Path

import pytest

from docflow.ingest import load
from docflow.models import Field, FieldStatus
from docflow.pipeline import corroborate
from docflow.rules import RuleValue, rule_extract

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic" / "invoices"
KEYS = ["supplier_gstin", "recipient_gstin", "invoice_no", "invoice_date", "taxable_total", "grand_total"]


def F(name, text, status=FieldStatus.GROUNDED):
    return Field(name=name, text=text, status=status, sources=["llm"])


def test_agreement_upgrades_to_verified():
    fields = {"grand_total": F("grand_total", "1,705.00")}
    corroborate(fields, {"grand_total": RuleValue("1705.00", ("w9",))})
    assert fields["grand_total"].status == FieldStatus.VERIFIED
    assert fields["grand_total"].sources == ["llm", "rules"]


def test_disagreement_is_conflict_with_both_values_kept():
    fields = {"grand_total": F("grand_total", "1,705.00")}
    corroborate(fields, {"grand_total": RuleValue("1,750.00", ("w9",))})
    f = fields["grand_total"]
    assert f.status == FieldStatus.CONFLICT and f.text == "1,705.00" and f.conflicts == {"rules": "1,750.00"}


def test_value_the_llm_missed_is_a_conflict():
    fields = {"invoice_no": F("invoice_no", None, FieldStatus.MISSING)}
    corroborate(fields, {"invoice_no": RuleValue("DFTEST-2627-0001", ("w3",))})
    assert fields["invoice_no"].status == FieldStatus.CONFLICT


def test_dates_and_ids_compare_by_meaning_not_by_spelling():
    fields = {"invoice_date": F("invoice_date", "04 Sep 2026"), "supplier_gstin": F("supplier_gstin", "27aaacu2414k1zf")}
    corroborate(fields, {"invoice_date": RuleValue("04 Sep 2026", ("w1",)), "supplier_gstin": RuleValue("27AAACU2414K1ZF", ("w2",))})
    assert fields["invoice_date"].status == fields["supplier_gstin"].status == FieldStatus.VERIFIED


def test_ungrounded_llm_value_is_never_upgraded():
    fields = {"grand_total": F("grand_total", "1,705.00", FieldStatus.UNGROUNDED)}
    corroborate(fields, {"grand_total": RuleValue("1,705.00", ("w9",))})
    assert fields["grand_total"].status == FieldStatus.UNGROUNDED


@pytest.mark.parametrize("split", ["dev", "heldout"])
def test_rule_extractor_is_never_wrong_on_digital_documents(split):
    """Precision is what matters: a wrong second source creates false conflicts.
    Held-out is included as a guard, but no rule was tuned on it (see RUN_LOG)."""
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))["documents"]
    wrong, produced, possible = [], 0, 0
    for d in manifest:
        if d["split"] != split or d["scan"] != "digital":
            continue
        truth = json.loads((DATA / f"{d['id']}.truth.json").read_text(encoding="utf-8"))["fields"]
        got = rule_extract(load(DATA / f"{d['id']}.pdf"))
        for k in KEYS:
            possible += 1
            if k in got:
                produced += 1
                if got[k].value != truth[k]:
                    wrong.append((d["id"], k, got[k].value, truth[k]))
    assert wrong == []
    assert produced / possible >= 0.85, f"coverage {produced}/{possible}"
