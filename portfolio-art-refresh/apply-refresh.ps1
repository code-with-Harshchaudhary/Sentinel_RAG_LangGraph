$ErrorActionPreference = 'Stop'
$refreshRoot = $PSScriptRoot
$portfolioRoot = 'C:\Users\Chaudhary\Desktop\upgrade'
$artRoot = 'C:\Users\Chaudhary\Desktop\Sentinel-RAG-Ops\output\imagegen'
$expectedRefreshHashes = @{
    'scripts\papers.mjs' = '1E77B2A3C44B781EE0F73CB278D7B187562DB87CFC7575271E5F90EB9A8F9881'
    'tests\papers.test.mjs' = '66B8277B4DD27DCB60783C619B21DC04704DAA197601FE3B0F5C487EC6CF8610'
}
$refreshFiles = @(
    @{ Source = (Join-Path $refreshRoot 'scripts\papers.mjs'); Target = 'scripts\papers.mjs' },
    @{ Source = (Join-Path $refreshRoot 'tests\papers.test.mjs'); Target = 'tests\papers.test.mjs' },
    @{ Source = (Join-Path $artRoot 'research-papers-default-v2.png'); Target = 'frontend\interface\public\work\research-papers-card-v2.png' },
    @{ Source = (Join-Path $artRoot 'research-papers-hover-v2.png'); Target = 'frontend\interface\public\work\research-papers-hover-v2.png' },
    @{ Source = (Join-Path $artRoot 'research-papers-prompts-v2.md'); Target = 'docs\research-papers-artwork-prompts-v2.md' }
)
foreach ($file in $refreshFiles) {
    $targetPath = [System.IO.Path]::GetFullPath((Join-Path $portfolioRoot $file.Target))
    if (-not $targetPath.StartsWith($portfolioRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Invalid target path' }
    if (-not (Test-Path -LiteralPath $file.Source -PathType Leaf)) { throw "Missing source: $($file.Source)" }
    if ($expectedRefreshHashes.ContainsKey($file.Target)) {
        if ((Get-FileHash -LiteralPath $targetPath -Algorithm SHA256).Hash -ne $expectedRefreshHashes[$file.Target]) { throw "Portfolio changed: $($file.Target)" }
    } elseif (Test-Path -LiteralPath $targetPath) { throw "New file already exists: $($file.Target)" }
}
foreach ($file in $refreshFiles) {
    Copy-Item -LiteralPath $file.Source -Destination (Join-Path $portfolioRoot $file.Target)
}
Write-Output 'Applied two revised images and their references. Original images preserved; report and layout unchanged.'
