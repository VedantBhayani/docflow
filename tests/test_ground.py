from docflow.ground import ground_ref
from docflow.models import Document, FieldStatus, Page, Word


def _doc(*texts: str) -> Document:
    words = [Word(id=f"w{i}", text=t, page=0, bbox=(0.1 * i, 0.2, 0.1 * i + 0.08, 0.22)) for i, t in enumerate(texts, 1)]
    return Document(path="x.pdf", sha256="0", pages=[Page(0, 595, 842, "pdf_text", words)])


DOC = _doc("GSTIN:", "27AAACU2414K1ZF", "Grand", "Total:", "1,23,45,678.90", "Meghdoot", "Packaging", "Pvt", "Ltd")
INDEX = {w.id: w for w in DOC.words()}


def test_value_spelled_by_its_words_is_grounded_with_evidence():
    f = ground_ref("supplier_gstin", "27AAACU2414K1ZF", ["w2"], INDEX)
    assert f.status == FieldStatus.GROUNDED
    assert f.evidence.page == 0
    assert f.evidence.bbox == INDEX["w2"].bbox


def test_words_that_do_not_spell_the_value_are_ungrounded():
    # LLM points at the right word but reports a different number.
    f = ground_ref("grand_total", "1,23,45,678.91", ["w5"], INDEX)
    assert f.status == FieldStatus.UNGROUNDED


def test_numbers_never_pass_on_fuzzy_similarity():
    # 14-char amounts differing in one digit are ~93% similar: must still fail.
    f = ground_ref("grand_total", "1,23,45,678.80", ["w5"], INDEX)
    assert f.status == FieldStatus.UNGROUNDED


def test_unknown_word_ids_are_ungrounded():
    f = ground_ref("invoice_no", "INV-1", ["w999"], INDEX)
    assert f.status == FieldStatus.UNGROUNDED


def test_absent_value_is_missing():
    assert ground_ref("irn", None, [], INDEX).status == FieldStatus.MISSING
    assert ground_ref("irn", "  ", [], INDEX).status == FieldStatus.MISSING


def test_span_including_a_label_still_grounds_the_value():
    f = ground_ref("supplier_gstin", "27AAACU2414K1ZF", ["w1", "w2"], INDEX)
    assert f.status == FieldStatus.GROUNDED
    assert f.match_score < 100


def test_multi_word_names_ground_and_evidence_spans_all_words():
    f = ground_ref("supplier_name", "Meghdoot Packaging Pvt Ltd", ["w6", "w7", "w8", "w9"], INDEX)
    assert f.status == FieldStatus.GROUNDED
    assert f.evidence.bbox[0] == INDEX["w6"].bbox[0]
    assert f.evidence.bbox[2] == INDEX["w9"].bbox[2]


def test_free_text_tolerates_minor_differences_but_ids_do_not():
    assert ground_ref("supplier_name", "Meghdoot Packaging Pvt. Ltd", ["w6", "w7", "w8", "w9"], INDEX).status == FieldStatus.GROUNDED
    assert ground_ref("supplier_gstin", "27AAACU2414K1ZE", ["w2"], INDEX).status == FieldStatus.UNGROUNDED


def test_value_must_be_whole_words_not_a_substring_of_a_word():
    doc = _doc("Qty", "16,026.62")
    idx = {w.id: w for w in doc.words()}
    assert ground_ref("lines.0.qty", "1", ["w2"], idx).status == FieldStatus.UNGROUNDED


def test_evidence_for_a_labelled_span_covers_only_the_value_words():
    f = ground_ref("supplier_gstin", "27AAACU2414K1ZF", ["w1", "w2"], INDEX)
    assert f.evidence.bbox == INDEX["w2"].bbox


def _row(*texts):
    words = [Word(id=f"w{i}", text=t, page=0, bbox=(0.05 * i, 0.5, 0.05 * i + 0.03, 0.52)) for i, t in enumerate(texts, 1)]
    return {w.id: w for w in words}


def test_incomplete_pointer_is_completed_when_the_exact_value_is_printed_next_to_it():
    idx = _row("Rate", "18", "%", "450.00")
    f = ground_ref("lines.0.gst_rate", "18 %", ["w2"], idx)
    assert f.status == FieldStatus.GROUNDED
    assert f.word_ids == ["w2", "w3"]
    assert f.match_score == 90.0


def test_completion_never_accepts_a_value_that_is_not_printed():
    idx = _row("Rate", "18", "GST", "450.00")
    assert ground_ref("lines.0.gst_rate", "18 %", ["w2"], idx).status == FieldStatus.UNGROUNDED


def test_completion_stays_on_the_same_visual_row():
    a = Word(id="w1", text="18", page=0, bbox=(0.1, 0.50, 0.13, 0.52))
    b = Word(id="w2", text="%", page=0, bbox=(0.1, 0.60, 0.13, 0.62))  # next line down
    assert ground_ref("lines.0.gst_rate", "18 %", ["w1"], {"w1": a, "w2": b}).status == FieldStatus.UNGROUNDED


def test_amount_corrected_from_ocr_noise_grounds_on_exact_numeric_equality():
    idx = _row("IGST:", "2.847.88")
    f = ground_ref("igst_total", "2,847.88", ["w2"], idx)
    assert f.status == FieldStatus.GROUNDED and f.match_score == 85.0


def test_numeric_grounding_still_rejects_a_different_number():
    idx = _row("IGST:", "2.847.88")
    assert ground_ref("igst_total", "2,847.89", ["w2"], idx).status == FieldStatus.UNGROUNDED


def test_numeric_grounding_only_applies_to_amount_fields():
    idx = _row("No:", "2.847.88")
    assert ground_ref("invoice_no", "2,847.88", ["w2"], idx).status == FieldStatus.UNGROUNDED


def test_numeric_grounding_finds_the_amount_inside_a_span_that_includes_its_label():
    idx = _row("Sub", "Total", "13.379.86")
    f = ground_ref("taxable_total", "13,379.86", ["w1", "w2", "w3"], idx)
    assert f.status == FieldStatus.GROUNDED and f.evidence.bbox == idx["w3"].bbox
