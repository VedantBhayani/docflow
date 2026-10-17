"""DocFlow review demo (Streamlit). Reads cached results from demo/data; needs no API key.

Run locally:  uv run --no-project --with-requirements demo/requirements.txt streamlit run demo/app.py
"""

import io
import json
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw

DATA = Path(__file__).parent / "data"
REPO = "https://github.com/VedantBhayani/docflow"
STATUS_COLOURS = {"VERIFIED": "#c7f0d2", "GROUNDED": "#e3efff", "CONFLICT": "#ffd6d6", "UNGROUNDED": "#ffe7c2", "MISSING": "#eeeeee"}
STATUS_HELP = {
    "VERIFIED": "found on the page AND confirmed by an independent source (the signed QR or a rule-based reader)",
    "GROUNDED": "found on the page exactly where the model said it is printed",
    "CONFLICT": "two independent sources disagree: a person must look",
    "UNGROUNDED": "the model returned a value that could not be found on the page: never trusted",
    "MISSING": "not printed on the document",
}

st.set_page_config(page_title="DocFlow: audit document review", layout="wide")


@st.cache_data
def load(doc_id: str) -> dict:
    return json.loads((DATA / f"{doc_id}.json").read_text(encoding="utf-8"))


@st.cache_data
def page_image(name: str) -> Image.Image:
    return Image.open(DATA / name).convert("RGB")


def field_rows(doc: dict) -> list[dict]:
    rows = [{"Field": k, "Value as printed": f["text"], "Status": f["status"], "Sources": ", ".join(f["sources"]),
             "_ev": f["evidence"]} for k, f in doc["fields"].items()]
    flagged = {name for f in doc["flags"] for name in f["fields"]}
    for i, line in enumerate(doc["lines"]):
        for k, f in line.items():
            # Invoices: every line value. Statements (hundreds of cells): the cells a Check points at.
            if doc["kind"] == "invoice" or f"lines.{i}.{k}" in flagged:
                rows.append({"Field": f"{'line' if doc['kind'] == 'invoice' else '⚠ row'} {i + 1} {k}", "Value as printed": f["text"],
                             "Status": f["status"], "Sources": ", ".join(f["sources"]), "_ev": f["evidence"]})
    return rows


def draw(doc: dict, page: int, boxes: list[dict], selected: dict | None) -> Image.Image:
    img = page_image(doc["demo"]["pages"][page]).copy()
    d = ImageDraw.Draw(img, "RGBA")
    w, h = img.size

    def rect(ev, outline, fill, width):
        x0, y0, x1, y1 = ev["bbox"]
        d.rectangle([x0 * w - 2, y0 * h - 2, x1 * w + 2, y1 * h + 2], outline=outline, fill=fill, width=width)

    for ev in boxes:
        if ev and ev["page"] == page:
            rect(ev, (37, 99, 235, 140), (37, 99, 235, 25), 1)
    if selected and selected["page"] == page:
        rect(selected, (220, 38, 38, 255), (250, 204, 21, 90), 3)
    return img


def excel(doc: dict, fields: pd.DataFrame, lines: pd.DataFrame, flags: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xl:
        fields.to_excel(xl, sheet_name="Fields", index=False)
        lines.to_excel(xl, sheet_name="Lines", index=False)
        flags.to_excel(xl, sheet_name="Flags", index=False)
    return buf.getvalue()


# ---------------------------------------------------------------- page
index = json.loads((DATA / "index.json").read_text(encoding="utf-8"))
st.title("DocFlow")
st.markdown(
    "**Reads GST invoices and bank statements, proves where every value is printed, and runs the checks an auditor would.** "
    "Pick a sample document: each value links to the words it was read from, and anything that fails a check is flagged for a person to review. "
    f"All documents here are synthetic. [Code and evaluation]({REPO})"
)

labels = {d["id"]: f"{'🟢' if d['status'] == 'CLEAN' else '🔴'}  {d['title']}" for d in index}
doc_id = st.selectbox("Sample document", list(labels), format_func=labels.get)
doc = load(doc_id)
blocking = [f for f in doc["flags"] if f["severity"] == "BLOCKING"]
warnings = [f for f in doc["flags"] if f["severity"] == "WARNING"]

if blocking:
    st.error(f"**NEEDS REVIEW**: {len(blocking)} blocking check(s) failed. {doc['demo']['note']}")
else:
    st.success(f"**CLEAN**: no blocking check failed. {doc['demo']['note']}")
if doc["demo"].get("trust_note") and doc.get("qr") and doc["qr"]["status"] != "NO_QR":
    st.caption(f"QR: **{doc['qr']['status']}**. {doc['demo']['trust_note']}")

fields = pd.DataFrame(field_rows(doc))
left, right = st.columns([5, 6], gap="large")
with left:
    st.subheader("Fields")
    st.caption("Click a row to see where it is printed.")
    shown = fields.drop(columns=["_ev"])
    styled = shown.style.apply(lambda col: [f"background-color: {STATUS_COLOURS.get(v, '')}; color: #111" for v in col], subset=["Status"])
    event = st.dataframe(styled, hide_index=True, use_container_width=True, height=440, on_select="rerun", selection_mode="single-row",
                         key=f"fields-{doc_id}")
    with st.expander("What the statuses mean"):
        for k, v in STATUS_HELP.items():
            st.markdown(f"<span style='background:{STATUS_COLOURS[k]};padding:1px 6px;border-radius:3px'>{k}</span> {v}", unsafe_allow_html=True)

rows = event.selection.rows if event and event.selection else []
selected = fields.iloc[rows[0]]["_ev"] if rows else None
n_pages = len(doc["demo"]["pages"])
with right:
    st.subheader("Document")
    default_page = selected["page"] if selected else 0
    page = st.radio("Page", list(range(n_pages)), index=default_page, horizontal=True, format_func=lambda p: f"{p + 1}",
                    key=f"page-{doc_id}-{default_page}") if n_pages > 1 else 0
    st.image(draw(doc, page, [r for r in fields["_ev"] if r], selected), use_container_width=True)
    if selected is not None and rows:
        r = fields.iloc[rows[0]]
        st.caption(f"Highlighted: **{r['Field']}** = `{r['Value as printed']}` ({r['Status']})")

st.subheader("Checks")
if not doc["flags"]:
    st.write("All checks passed.")
for f in blocking:
    st.markdown(f"🔴 **{f['check_id']}**: {f['message']}")
for f in warnings:
    st.markdown(f"🟡 **{f['check_id']}** (warning): {f['message']}")

if doc["kind"] == "statement":
    st.subheader("Statement Lines")
    st.caption("The normalised rows a reconciliation step consumes: channel, reference (UTR/RRN), direction, amount.")
    lines = pd.DataFrame(doc["statement_lines"])[["line_no", "txn_date", "channel", "ref_no", "counterparty_hint", "direction", "amount", "balance", "flag_ids"]]
    lines["flag_ids"] = lines["flag_ids"].apply(lambda x: ", ".join(x))
    st.dataframe(lines, hide_index=True, use_container_width=True, height=360)
else:
    lines = pd.DataFrame([{k: f["text"] for k, f in line.items()} for line in doc["lines"]])
    st.subheader("Line items")
    st.dataframe(lines, hide_index=True, use_container_width=True)

flags_df = pd.DataFrame(doc["flags"] or [], columns=["check_id", "severity", "message", "fields"])
flags_df["fields"] = flags_df["fields"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
st.download_button("Download Excel (Fields, Lines, Flags)", excel(doc, shown, lines, flags_df), file_name=f"{doc_id}-docflow.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
st.caption(f"Model: {doc['llm'].get('model')} · prompt {doc['llm'].get('prompt_version')} · source {doc['path']}")
