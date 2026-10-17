"""Guards against a bug that bit twice: a regex's \\b written through a nested string
became a literal backspace character, silently breaking the pattern."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"\n", "\t", "\r"}


def test_no_control_characters_in_source_or_prompts():
    bad = []
    for folder in ("src", "tests", "prompts"):
        for path in (ROOT / folder).rglob("*"):
            if path.suffix not in {".py", ".md"}:
                continue
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if any(ord(ch) < 32 and ch not in ALLOWED for ch in line):
                    bad.append(f"{path.relative_to(ROOT)}:{n}")
    assert bad == []
