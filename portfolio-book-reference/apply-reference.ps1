$ErrorActionPreference = 'Stop'
$referenceRoot = $PSScriptRoot
$portfolioRoot = 'C:\Users\Chaudhary\Desktop\upgrade'
$artRoot = 'C:\Users\Chaudhary\Desktop\Sentinel-RAG-Ops\output\imagegen'
$expectedReferenceHashes = @{
    'scripts\papers.mjs' = '1E77B2A3C44B781EE0F73CB278D7B187562DB87CFC7575271E5F90EB9A8F9881'
    'tests\papers.test.mjs' = '66B8277B4DD27DCB60783C619B21DC04704DAA197601FE3B0F5C487EC6CF8610'
}
$referenceFiles = @(
    @{ Source = (Join-Path $referenceRoot 'scripts\papers.mjs'); Target = 'scripts\papers.mjs' },
    @{ Source = (Join-Path $referenceRoot 'tests\papers.test.mjs'); Target = 'tests\papers.test.mjs' },
    @{ Source = (Join-Path $artRoot 'rag-connected-knowledge-closed.png'); Target = 'frontend\interface\public\work\rag-connected-knowledge-closed.png' },
    @{ Source = (Join-Path $artRoot 'rag-connected-knowledge-open.png'); Target = 'frontend\interface\public\work\rag-connected-knowledge-open.png' },
    @{ Source = (Join-Path $artRoot 'rag-connected-knowledge-prompts.md'); Target = 'docs\rag-connected-knowledge-artwork-prompts.md' }
)
foreach ($file in $referenceFiles) {
    $targetPath = [System.IO.Path]::GetFullPath((Join-Path $portfolioRoot $file.Target))
    if (-not $targetPath.StartsWith($portfolioRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Invalid target path' }
    if (-not (Test-Path -LiteralPath $file.Source -PathType Leaf)) { throw "Missing source: $($file.Source)" }
    if ($expectedReferenceHashes.ContainsKey($file.Target)) {
        if ((Get-FileHash -LiteralPath $targetPath -Algorithm SHA256).Hash -ne $expectedReferenceHashes[$file.Target]) { throw "Portfolio changed: $($file.Target)" }
    } elseif (Test-Path -LiteralPath $targetPath) { throw "New file already exists: $($file.Target)" }
}
foreach ($file in $referenceFiles) {
    Copy-Item -LiteralPath $file.Source -Destination (Join-Path $portfolioRoot $file.Target)
}
Write-Output 'Applied the white RAG book closed/open pair. Report, layout, and old images preserved.'
