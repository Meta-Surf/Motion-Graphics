$ErrorActionPreference='Stop'
$script=Join-Path $PSScriptRoot 'start-voice-gpu.ps1'
if(-not(Test-Path $script)){throw "Missing $script"}
$startup=[Environment]::GetFolderPath('Startup')
$link=Join-Path $startup 'Motion Graphics - VoiceStudio GPU.lnk'
$shell=New-Object -ComObject WScript.Shell
$shortcut=$shell.CreateShortcut($link)
$shortcut.TargetPath=Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$shortcut.Arguments='-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "'+$script+'" -KeepAlive'
$shortcut.WorkingDirectory=Split-Path $PSScriptRoot -Parent
$shortcut.WindowStyle=7
$shortcut.Description='Starts the existing WSL ROCm VoiceStudio service and keeps WSL alive.'
$shortcut.Save()
& wsl.exe -d Ubuntu-24.04 -u root --exec systemctl enable voicestudio-gpu
if($LASTEXITCODE -ne 0){throw 'Cannot enable VoiceStudio GPU service'}
Write-Output "Installed per-user logon startup: $link"
& $script
