"""LLM extraction: locate printed values and the word IDs behind them.

Responses are cached by content (serialised words + prompt version + model), so
evaluation reruns make no API calls. Every call is appended to a prompt trace.
"""

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "prompts"
CACHE = ROOT / "data" / "llm_cache"  # committed: responses about synthetic documents only, no secrets
TRACE = ROOT / "results" / "traces" / "prompt_trace.jsonl"
MODEL = "mistral-small-2603"  # Mistral Small 4, pinned (RUN_LOG 2026-10-17)
FALLBACK_MODEL = "ministral-14b-2512"


class Ref(BaseModel):
    text: str | None = Field(description="Value exactly as printed, or null if not printed")
    word_ids: list[str] = Field(description="IDs of the words making up the value, in reading order")


class LineRef(BaseModel):
    description: Ref
    hsn: Ref
    qty: Ref
    uqc: Ref
    unit_price: Ref
    taxable_value: Ref
    gst_rate: Ref
    cgst: Ref
    sgst: Ref
    igst: Ref


class InvoiceExtraction(BaseModel):
    supplier_name: Ref
    supplier_address: Ref
    supplier_gstin: Ref
    recipient_name: Ref
    recipient_address: Ref
    recipient_gstin: Ref
    invoice_no: Ref
    invoice_date: Ref
    place_of_supply: Ref
    reverse_charge: Ref
    irn: Ref
    taxable_total: Ref
    cgst_total: Ref
    sgst_total: Ref
    igst_total: Ref
    round_off: Ref
    grand_total: Ref
    lines: list[LineRef]


SCHEMAS = {"invoice": (InvoiceExtraction, "invoice.v3")}


def _client():
    load_dotenv(ROOT / ".env")
    key = os.environ.get("MISTRAL_API_KEY")
    if not key:
        raise RuntimeError("MISTRAL_API_KEY is not set in docflow/.env")
    from mistralai.client import Mistral

    return Mistral(api_key=key)


def extract(kind: str, serialised: str, model: str = MODEL) -> tuple[BaseModel, dict]:
    """Return the parsed extraction and call metadata (cache hit, usage, seconds)."""
    schema, prompt_version = SCHEMAS[kind]
    system = (PROMPTS / f"{prompt_version}.md").read_text(encoding="utf-8")
    key = hashlib.sha256("\n".join([prompt_version, model, system, serialised]).encode()).hexdigest()
    cached = CACHE / f"{key}.json"
    if cached.exists():
        record = json.loads(cached.read_text(encoding="utf-8"))
        return schema.model_validate(record["parsed"]), {**record["meta"], "cache_hit": True}

    t0 = time.perf_counter()
    res = _client().chat.parse(
        model=model,
        temperature=0,
        response_format=schema,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": serialised}],
    )
    parsed = res.choices[0].message.parsed
    if parsed is None:
        raise RuntimeError(f"{model} returned no parseable {kind} extraction")
    meta = {
        "model": model,
        "prompt_version": prompt_version,
        "seconds": round(time.perf_counter() - t0, 2),
        "prompt_tokens": res.usage.prompt_tokens if res.usage else None,
        "completion_tokens": res.usage.completion_tokens if res.usage else None,
        "cache_key": key,
    }
    CACHE.mkdir(parents=True, exist_ok=True)
    cached.write_text(json.dumps({"parsed": parsed.model_dump(), "meta": meta}, indent=1), encoding="utf-8")
    TRACE.parent.mkdir(parents=True, exist_ok=True)
    with TRACE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "kind": kind, **meta,
            "input_sha256": hashlib.sha256(serialised.encode()).hexdigest(),
            "raw_response": res.choices[0].message.content,
        }) + "\n")
    return parsed, {**meta, "cache_hit": False}
