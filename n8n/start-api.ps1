# Start the DocFlow API for the intake workflow.
# The synthetic test invoices carry QR codes signed with DocFlow's TEST key, so the demo runs in test trust mode.
# For real e-invoices, drop DOCFLOW_TRUST (the default 'nic' verifies against NIC's published certificates).
param([string]$Trust = 'test')
Set-Location (Join-Path $PSScriptRoot '..')
$env:DOCFLOW_TRUST = $Trust
& .\.venv\Scripts\python.exe -m uvicorn docflow.api:app --port 8000
