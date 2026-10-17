# Start n8n for the DocFlow intake workflow (n8n 2.43.7, npm global install).
# Run the DocFlow API first:  uv run uvicorn docflow.api:app --port 8000
$work = Join-Path $PSScriptRoot 'work'
foreach ($d in 'inbox\invoices', 'inbox\statements', 'processed', 'review', 'failed', 'out') {
    New-Item -ItemType Directory -Force (Join-Path $work $d) | Out-Null
}
$env:DOCFLOW_WORK = $work
# n8n 2.x disables Local File Trigger by default; this list re-enables it and keeps Execute Command blocked.
$env:NODES_EXCLUDE = '["n8n-nodes-base.executeCommand"]'
# File nodes may touch only the work folder.
$env:N8N_RESTRICT_FILE_ACCESS_TO = $work
# The Code nodes read DOCFLOW_WORK and use Node's fs/path to move files and append the register.
$env:N8N_BLOCK_ENV_ACCESS_IN_NODE = 'false'
$env:NODE_FUNCTION_ALLOW_BUILTIN = 'fs,path'
n8n start
