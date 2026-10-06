param([string]$OutputDirectory = '.qa/phase6-render')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$renderRoot = [System.IO.Path]::GetFullPath((Join-Path $projectRoot $OutputDirectory))
New-Item -ItemType Directory -Path $renderRoot -Force | Out-Null
$word = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $results = @()
    foreach ($baseName in @('TONG_QUAN_DU_AN', 'HUONG_DAN_SU_DUNG')) {
        $sourcePath = Join-Path $projectRoot ('docs/' + $baseName + '.docx')
        $pdfPath = Join-Path $renderRoot ($baseName + '.pdf')
        $doc = $null
        try {
            $doc = $word.Documents.Open($sourcePath, $false, $false)
            $doc.Fields.Update() | Out-Null
            $doc.TablesOfContents | ForEach-Object { $_.Update() }
            $doc.Repaginate()
            $doc.TablesOfContents | ForEach-Object { $_.UpdatePageNumbers() }
            $doc.Save()
            $doc.ExportAsFixedFormat($pdfPath, 17)
            $results += @{file = ('docs/' + $baseName + '.docx'); pages = $doc.ComputeStatistics(2); pdf = $pdfPath}
        } finally {
            if ($null -ne $doc) { $doc.Close(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($doc) }
        }
    }
    $results | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $renderRoot 'word-render.json') -Encoding utf8
    $results | ConvertTo-Json -Depth 4
} finally {
    if ($null -ne $word) { $word.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word) }
}
