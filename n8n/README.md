# DocFlow intake workflow (n8n)

Drop a PDF in a folder, and it is extracted, checked, filed and logged in an Excel register. No one runs a script.

![workflow](workflow.png)

| Step | Node | What it does |
|---|---|---|
| 1 | **New file in inbox** (Local File Trigger) | Watches `work/inbox/invoices/` and `work/inbox/statements/`. The sub-folder decides the document kind. |
| 2 | **DocFlow /extract** (HTTP Request) | `POST http://127.0.0.1:8000/extract` with the PDF. Returns Fields, Evidence, Flags and the `blocking` list. |
| 3 | **Any blocking flag?** (IF) | No: **CLEAN**, moved to `processed/`. Yes: **NEEDS REVIEW**, moved to `review/` with the reasons. |
| 4 | Error output | API down, not a PDF, or an unreadable PDF: **FAILED**, moved to `failed/` with the error text. |
| 5 | **Route and register**, **To Excel** | Appends one row to `out/register.jsonl` and rewrites `out/register.xlsx` from all rows. Each row records the file, kind, status, blocking checks, why, key fields, QR status and where the file went. |

Everything stays on the machine. There are no credentials in the workflow; the only secret is the Mistral key in `docflow/.env`, which the API reads.

## Run it (Windows, PowerShell)

Needs Node 20.19–24.x. Tested with Node 24.11.1 and n8n 2.43.7.

```powershell
npm install -g n8n@2.43.7
```

Terminal 1, the API (from `docflow/`):

```powershell
uv run uvicorn docflow.api:app --port 8000
```

Terminal 2, n8n:

```powershell
powershell -ExecutionPolicy Bypass -File n8n\start-n8n.ps1
```

Then, at http://localhost:5678:
1. Create the owner account (it is local only).
2. Import `n8n/docflow-intake.json`.
3. Publish (activate) the workflow.

Or use the CLI before starting:

```powershell
n8n import:workflow --input=n8n\docflow-intake.json
```

Then copy PDFs into `n8n\work\inbox\invoices\` or `n8n\work\inbox\statements\`.

### Why the start script sets these variables

| Variable | Why |
|---|---|
| `NODES_EXCLUDE=["n8n-nodes-base.executeCommand"]` | n8n 2.x disables Local File Trigger by default. This list re-enables it and keeps Execute Command blocked. |
| `N8N_RESTRICT_FILE_ACCESS_TO=<work>` | File nodes can touch only the work folder. |
| `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`, `NODE_FUNCTION_ALLOW_BUILTIN=fs,path` | The Code node reads `DOCFLOW_WORK` and moves files and appends the register with Node's `fs`. |
