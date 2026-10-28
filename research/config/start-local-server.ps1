$taskRuntime = Join-Path $env:LOCALAPPDATA 'BankingDefenseRuntime'
try {
    $taskExisting = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/version' -TimeoutSec 2 -ErrorAction Stop
    Write-Output "Local Ollama already listening: $($taskExisting.version)"
    return
} catch { }
$taskProject = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$taskLog = Join-Path $taskProject 'research\runs\rebuild-20261027\evidence'
New-Item -ItemType Directory -Path $taskLog -Force | Out-Null
$env:OLLAMA_HOST = '127.0.0.1:11434'
$env:OLLAMA_MODELS = Join-Path $taskRuntime 'models'
$env:OLLAMA_NO_CLOUD = '1'
$env:OLLAMA_CONTEXT_LENGTH = '8192'
$env:OLLAMA_NUM_PARALLEL = '1'
$env:OLLAMA_MAX_LOADED_MODELS = '1'
$env:OLLAMA_FLASH_ATTENTION = '1'
$env:OLLAMA_KV_CACHE_TYPE = 'q8_0'
$env:OLLAMA_VULKAN = '0'
$taskStamp = Get-Date -Format 'yyyyMMddTHHmmss'
$taskProcess = Start-Process -FilePath (Join-Path $taskRuntime 'ollama-0.40.11\ollama.exe') -ArgumentList 'serve' -WindowStyle Hidden -RedirectStandardOutput (Join-Path $taskLog "ollama-$taskStamp-stdout.log") -RedirectStandardError (Join-Path $taskLog "ollama-$taskStamp-stderr.log") -PassThru
$taskProcess.Id | Set-Content -LiteralPath (Join-Path $taskLog 'ollama-service.pid') -Encoding UTF8
Write-Output "Local Ollama process: $($taskProcess.Id)"
