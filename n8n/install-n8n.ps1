# Clean any half-finished global install, then install the pinned n8n. Log: .scratch/logs/n8n_install.log
$log = Join-Path $PSScriptRoot '..\..\.scratch\logs\n8n_install.log'
$mods = Join-Path $env:APPDATA 'npm\node_modules'
"cleaning partial install $(Get-Date)" | Out-File $log
Get-ChildItem $mods -Force -Filter '.n8n-*' -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
if (Test-Path (Join-Path $mods 'n8n')) { cmd /c rmdir /s /q (Join-Path $mods 'n8n') }
"installing $(Get-Date)" | Out-File -Append $log
npm install -g n8n@2.43.7 --no-audit --no-fund *>> $log
"NPM EXIT $LASTEXITCODE $(Get-Date)" | Out-File -Append $log
