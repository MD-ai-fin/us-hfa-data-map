<#
.SYNOPSIS
  Export all 4 FY2025 analysis report .docx sources to accessible (tagged) PDFs.

.DESCRIPTION
  Thin orchestrator around export_one_report_pdf.ps1. Each language is run
  as its own separate `powershell -File` child process (rather than looping
  over documents inside one shared Word.Application instance) -- looping
  inside a single Word COM session was observed to hang unpredictably
  during development, while one Word.Application per process, run once and
  quit, was reliable every time. Slower (~4 Word startups instead of 1) but
  actually finishes.

  Requires a local installation of Microsoft Word (COM automation) on
  Windows -- this cannot run on GitHub Actions / a Linux CI box, matching
  the project's existing pattern of manually-run local build scripts.

  Run docs/generate_report_docx_i18n.py first if the ES/PL .docx sources
  under FY2025/ are missing or stale. Run docs/postprocess_report_pdfs.py
  afterwards to patch in the PDF /Title and /Lang metadata (Word's COM
  automation does not reliably set these in this environment) and get a
  basic tagging sanity report.

.OUTPUTS
  docs/reports/fy2025-en.pdf
  docs/reports/fy2025-zh.pdf
  docs/reports/fy2025-es.pdf
  docs/reports/fy2025-pl.pdf
#>

$ErrorActionPreference = "Stop"

$docsDir = $PSScriptRoot
$root = Split-Path -Parent $docsDir
$fy2025Dir = Join-Path $root "FY2025"
$outDir = Join-Path $docsDir "reports"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

# Locate source .docx by (encoding-safe) filename pattern rather than
# embedding the Chinese filename literally in this script.
$allDocx = Get-ChildItem -Path (Join-Path $fy2025Dir "*.docx")
$enDocx = $allDocx | Where-Object { $_.Name -like "FY2025_US_State_HFA_ACFR_Analysis_Report.docx" }
$esDocx = $allDocx | Where-Object { $_.Name -like "*_ES.docx" }
$plDocx = $allDocx | Where-Object { $_.Name -like "*_PL.docx" }
$zhDocx = $allDocx | Where-Object { $_.Name -notlike "FY2025_US_State*" }

if (-not $enDocx) { throw "English source .docx not found under $fy2025Dir" }
if (-not $zhDocx) { throw "Chinese source .docx not found under $fy2025Dir" }
if (-not $esDocx) { throw "Spanish source .docx not found -- run docs/generate_report_docx_i18n.py first" }
if (-not $plDocx) { throw "Polish source .docx not found -- run docs/generate_report_docx_i18n.py first" }

# WdLanguageID values (stable Windows LCIDs): English (US), Chinese
# (Simplified, PRC), Spanish (International Sort / Spain), Polish.
$jobs = @(
  @{ Docx = $enDocx.FullName; Pdf = Join-Path $outDir "fy2025-en.pdf"; Lcid = 1033 },
  @{ Docx = $zhDocx.FullName; Pdf = Join-Path $outDir "fy2025-zh.pdf"; Lcid = 2052 },
  @{ Docx = $esDocx.FullName; Pdf = Join-Path $outDir "fy2025-es.pdf"; Lcid = 3082 },
  @{ Docx = $plDocx.FullName; Pdf = Join-Path $outDir "fy2025-pl.pdf"; Lcid = 1045 }
)

$exportScript = Join-Path $docsDir "export_one_report_pdf.ps1"
$failed = @()

foreach ($job in $jobs) {
  Write-Host "=== $($job.Pdf) ==="
  & powershell -ExecutionPolicy Bypass -File $exportScript -DocxPath $job.Docx -PdfPath $job.Pdf -Lcid $job.Lcid
  if ($LASTEXITCODE -ne 0 -or -not (Test-Path $job.Pdf)) {
    Write-Host "  FAILED: $($job.Pdf)"
    $failed += $job.Pdf
  } else {
    Write-Host "  OK: $($job.Pdf)"
  }
}

if ($failed.Count -gt 0) {
  throw "Failed to export: $($failed -join ', ')"
}

Write-Host "Done. Now run: python docs/postprocess_report_pdfs.py"
