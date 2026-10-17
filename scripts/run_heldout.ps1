# One-time final held-out evaluation (ticket 10). Results go to results/<date>/heldout*.
Set-Location (Join-Path $PSScriptRoot '..')
$log = Join-Path $PSScriptRoot '..\..\.scratch\logs\heldout.log'
& .\.venv\Scripts\python.exe -m docflow.evaluate --split heldout --final --kind invoice *> $log
"INVOICE EXIT $LASTEXITCODE" | Out-File -Append $log
& .\.venv\Scripts\python.exe -m docflow.evaluate --split heldout --final --kind statement *>> $log
"STATEMENT EXIT $LASTEXITCODE" | Out-File -Append $log
"HELD-OUT DONE" | Out-File -Append $log
