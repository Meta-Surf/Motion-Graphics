param([switch]$KeepAlive)
$ErrorActionPreference='Stop'
$wsl=Join-Path $env:SystemRoot 'System32\wsl.exe'
if($KeepAlive){
  # A systemd service alone does not keep a WSL distribution alive.
  & $wsl -d Ubuntu-24.04 -u root --exec /bin/bash -lc 'systemctl start voicestudio-gpu; exec sleep infinity'
  exit $LASTEXITCODE
}
$existing=Get-CimInstance Win32_Process -Filter "Name='wsl.exe'" | Where-Object {$_.CommandLine -like '*voicestudio-gpu*sleep infinity*'}
if(-not $existing){
  Start-Process powershell.exe -WindowStyle Hidden -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',('"'+$PSCommandPath+'"'),'-KeepAlive')
}
for($attempt=0;$attempt -lt 45;$attempt++){
  try {
    $health=Invoke-RestMethod 'http://127.0.0.1:3901/health' -TimeoutSec 2
    if($health.status -eq 'ok' -and $health.device -match 'AMD' -and $health.device -notmatch 'cpu'){ $health | ConvertTo-Json; exit 0 }
  } catch {}
  Start-Sleep -Seconds 1
}
throw 'VoiceStudio GPU did not become ready on port 3901; CPU fallback is not permitted.'
