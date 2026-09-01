$ErrorActionPreference = 'Stop'
$integrationRoot = $PSScriptRoot
$targetRoot = [System.IO.Path]::GetFullPath('C:\Users\Chaudhary\Desktop\upgrade')
$expected = @{
    'scripts\build.mjs' = '2254F1B648E5477DA0ACCF04F9B62075B1710C31BF85D6579A12490B3550C021'
    'backend\worker\index.js' = 'A543A39A617F1EB6BACB9F35D27D18392816CE501C0B8E405D2EA4D49F3BB97B'
    'README.md' = '897A53638F58DEE687B57F1B49C7BD72CE640DBA0DECD81973CE2C37EE9F6D27'
}
$paths = @(
    'scripts\build.mjs', 'scripts\papers.mjs', 'backend\worker\index.js', 'README.md',
    'frontend\interface\papers.json', 'frontend\interface\public\papers\papers.css',
    'frontend\interface\public\papers\papers.js', 'frontend\interface\public\papers\theme.js',
    'frontend\interface\public\papers\card-link.js', 'tests\papers.test.mjs',
    'frontend\interface\public\papers\files\sentinel-rag-ops.pdf',
    'frontend\interface\public\papers\files\sentinel-rag-ops.docx',
    'frontend\interface\public\papers\files\langfuse-rag-ops.pdf',
    'frontend\interface\public\papers\files\langfuse-rag-ops.docx',
    'frontend\interface\public\work\research-papers-card.png',
    'frontend\interface\public\work\research-papers-hover.png',
    'docs\research-papers-artwork-prompts.md'
)
foreach ($relative in $paths) {
    $destination = [System.IO.Path]::GetFullPath((Join-Path $targetRoot $relative))
    if (-not $destination.StartsWith($targetRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Target escapes project' }
    if (-not (Test-Path -LiteralPath (Join-Path $integrationRoot $relative) -PathType Leaf)) { throw "Missing staged file: $relative" }
    if ($expected.ContainsKey($relative)) {
        if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash -ne $expected[$relative]) { throw "Source changed during preparation: $relative" }
    } elseif (Test-Path -LiteralPath $destination) { throw "Refusing to overwrite an existing new asset: $relative" }
}
foreach ($relative in $paths) {
    $destination = Join-Path $targetRoot $relative
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
    Copy-Item -LiteralPath (Join-Path $integrationRoot $relative) -Destination $destination
}
Write-Output "Applied $($paths.Count) scoped files to the existing portfolio. No files removed."
