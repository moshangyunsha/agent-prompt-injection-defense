param([string]$InputPath = '', [string]$OutputDir = '')
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
if (-not $InputPath) { $InputPath = Join-Path $root 'output\presentation.pptx' }
if (-not $OutputDir) { $OutputDir = Join-Path $root 'output\previews' }
$InputPath = (Resolve-Path -LiteralPath $InputPath).Path
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
$app = New-Object -ComObject PowerPoint.Application
$deck = $null
try {
  $deck = $app.Presentations.Open($InputPath, $true, $false, $false)
  $count = $deck.Slides.Count
  for ($i = 1; $i -le $count; $i++) {
    $path = Join-Path $OutputDir ('slide{0:D2}.png' -f $i)
    $deck.Slides.Item($i).Export($path, 'PNG', 1600, 900)
    if (-not (Test-Path -LiteralPath $path)) { throw "Missing export $path" }
  }
  @{ slides = $count; input = $InputPath; width = 1600; height = 900 } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $OutputDir 'render-metadata.json') -Encoding UTF8
  Write-Output "PowerPoint opened the deck and exported $count slides."
}
finally {
  if ($deck -ne $null) { $deck.Close() }
  $app.Quit()
}
