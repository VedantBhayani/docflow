"""Tracer bullet: one synthetic digital invoice, end to end, against its truth file.

Runs offline from the committed LLM cache. With no cache entry and no API key it skips.
"""

import json
import random

import pytest

from docflow.pipeline import process
from docflow.synth.invoice import build_spec, write_invoice


@pytest.fixture(scope="module")
def tracer(tmp_path_factory):
    out = tmp_path_factory.mktemp("tracer")
    pdf, truth = write_invoice(build_spec(random.Random(7), 42, n_lines=3), out, "inv-tracer-0042")
    try:
        result = process(pdf)
    except RuntimeError as exc:
        if "MISTRAL_API_KEY" in str(exc):
            pytest.skip("no cached response and no API key")
        raise
    return result, json.loads(truth.read_text(encoding="utf-8")), pdf


def test_every_header_field_matches_truth_and_is_grounded(tracer):
    result, truth, _ = tracer
    for name, printed in truth["fields"].items():
        f = result.fields[name]
        assert (f.text, f.status) == (printed, "GROUNDED"), name
        assert f.evidence is not None and 0 <= f.evidence.bbox[0] < f.evidence.bbox[2] <= 1


def test_every_line_item_matches_truth(tracer):
    result, truth, _ = tracer
    assert len(result.lines) == len(truth["lines"])
    for got, want in zip(result.lines, truth["lines"]):
        for name, printed in want.items():
            assert (got[name].text, got[name].status) == (printed, "GROUNDED"), name


def test_clean_invoice_is_clean(tracer):
    result, _, _ = tracer
    assert result.status == "CLEAN"
    assert result.flags == []


def test_rerun_is_served_from_cache(tracer):
    _, _, pdf = tracer
    assert process(pdf).llm["cache_hit"] is True
