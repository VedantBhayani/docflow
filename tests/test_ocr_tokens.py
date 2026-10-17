from docflow.ingest import split_glued_labels
from docflow.models import Word


def W(i, text, x0=0.1, x1=0.5):
    return Word(id=f"w{i}", text=text, page=0, bbox=(x0, 0.2, x1, 0.22), confidence=0.99)


def test_label_glued_to_value_is_split_into_two_words():
    out = split_glued_labels([W(1, "GSTIN:07RADCT5913R3Z8", 0.1, 0.5)])
    assert [w.text for w in out] == ["GSTIN:", "07RADCT5913R3Z8"]
    assert out[0].bbox[0] == 0.1 and out[1].bbox[2] == 0.5 and out[0].bbox[2] == out[1].bbox[0]
    assert all(w.confidence == 0.99 for w in out)


def test_ordinary_tokens_are_untouched():
    words = [W(1, "GSTIN:"), W(2, "27AAACU2414K1ZF"), W(3, "12:30"), W(4, "https://x"), W(5, "Rs.1,200.00")]
    assert [w.text for w in split_glued_labels(words)] == ["GSTIN:", "27AAACU2414K1ZF", "12:30", "https://x", "Rs.1,200.00"]


def test_glued_label_with_stray_punctuation_is_split_and_cleaned():
    out = split_glued_labels([W(1, "GSTIN:-33LDWCN5287F1ZG"), W(2, "GSTIN:.19OPQCA9108Q1ZI")])
    assert [w.text for w in out] == ["GSTIN:", "33LDWCN5287F1ZG", "GSTIN:", "19OPQCA9108Q1ZI"]
