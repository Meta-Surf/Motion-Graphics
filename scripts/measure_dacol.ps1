# Measure an explicitly selected command. Counters are system-wide, not attribution.
param([Parameter(Mandatory=$true)][string]$OutputDirectory,
      [Parameter(Mandatory=$true)][string]$Executable,
      [Parameter(Mandatory=$true)][string[]]$CommandArguments)
$ErrorActionPreference='Stop'
if(Test-Path $OutputDirectory){throw 'Choose a new measurement directory'}
New-Item -ItemType Directory -Path $OutputDirectory | Out-Null
$root=Resolve-Path $OutputDirectory
$watch=[Diagnostics.Stopwatch]::StartNew()
# Start-Process uses a Windows command line. Quote every argument and reject quotes.
$quoted=@($CommandArguments | ForEach-Object {if($_.Contains('"')){throw 'Embedded quotes unsupported'}; '"'+$_+'"'})
$child=Start-Process -FilePath $Executable -ArgumentList $quoted -PassThru -NoNewWindow -RedirectStandardOutput "$root/stdout.log" -RedirectStandardError "$root/stderr.log"
$retainedHandle=$child.Handle # Retain the process handle so ExitCode survives Refresh on Windows PowerShell.
$samples=@()
do {
    $sample=[ordered]@{elapsed_seconds=[math]::Round($watch.Elapsed.TotalSeconds,3);cpu_percent=$null;gpu_engine_peak_percent=$null;dedicated_gpu_bytes=$null;root_working_set_bytes=$null;counter_error=$null}
    try {
        $sample.cpu_percent=(Get-CimInstance Win32_PerfFormattedData_PerfOS_Processor -Filter "Name='_Total'").PercentProcessorTime
        $engines=Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine
        $sample.gpu_engine_peak_percent=($engines | Measure-Object UtilizationPercentage -Maximum).Maximum
        $memory=Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUAdapterMemory
        $sample.dedicated_gpu_bytes=($memory | Measure-Object DedicatedUsage -Sum).Sum
        $child.Refresh();if(!$child.HasExited){$sample.root_working_set_bytes=$child.WorkingSet64}
    } catch {$sample.counter_error=$_.Exception.GetType().Name}
    $samples+=[pscustomobject]$sample
    if($watch.Elapsed.TotalSeconds -gt 300){$child.Kill();throw 'Diagnostic timeout after 300 seconds'}
    Start-Sleep -Milliseconds 500
    $child.Refresh()
} while(!$child.HasExited)
$child.WaitForExit();$watch.Stop()
$report=[ordered]@{seconds=[math]::Round($watch.Elapsed.TotalSeconds,3);exit_code=$child.ExitCode;scope='System counters include concurrent work; root RSS excludes renderer children. Dedicated usage is driver allocation, not tensor peak. Missing values are unmeasured.';samples=$samples}
$report | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 "$root/measurements.json"
$report | Select-Object seconds,exit_code,scope | ConvertTo-Json
exit $child.ExitCode
