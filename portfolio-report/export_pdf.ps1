$ErrorActionPreference = 'Stop'
$reportRoot = Split-Path -Parent $PSScriptRoot
$reportDocx = Join-Path $reportRoot 'output\docx\Sentinel_RAG_Ops_Portfolio_Report.docx'
$reportPdf = Join-Path $reportRoot 'output\pdf\Sentinel_RAG_Ops_Portfolio_Report.pdf'
$reportWord = $null
$reportDocument = $null
try {
    $reportWord = New-Object -ComObject Word.Application
    $reportWord.Visible = $false
    $reportWord.DisplayAlerts = 0
    $reportDocument = $reportWord.Documents.Open($reportDocx, $false, $true)
    $reportDocument.Repaginate()
    $reportPages = $reportDocument.ComputeStatistics(2)
    $reportDocument.ExportAsFixedFormat($reportPdf, 17)
    Write-Output "Exported PDF with $reportPages pages: $reportPdf"
}
finally {
    if ($null -ne $reportDocument) {
        $reportDocument.Close(0)
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($reportDocument)
    }
    if ($null -ne $reportWord) {
        $reportWord.Quit()
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($reportWord)
    }
}
