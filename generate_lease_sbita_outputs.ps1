# Generate Word report and Excel workbook from lease_sbita_extracted_data.json
$base = "c:\Users\may_d\ACFR"
$jsonPath = Join-Path $base "lease_sbita_extracted_data.json"
$excelPath = Join-Path $base "Lease_SBITA_Liability_SN_P_by_State_FY2024_FY2025.xlsx"
$wordPath = Join-Path $base "Lease_SBITA_Governmental_Funds_Reporting_Report.docx"

$data = Get-Content $jsonPath -Raw | ConvertFrom-Json

function Format-Amt($v) {
    if ($null -eq $v) { return "N/A" }
    return [math]::Round([double]$v, 0).ToString("N0")
}

# --- Excel ---
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
if (Test-Path $excelPath) { Remove-Item $excelPath -Force }
$wb = $excel.Workbooks.Add()
$ws = $wb.Worksheets.Item(1)
$ws.Name = "Lease SBITA SNP Data"

$headers = @(
    "State","Agency","Fiscal Year","Reporting Format","Gov-Wide SNP?",
    "Lease - Governmental Activities","Lease - Business-Type Activities","Lease - Total",
    "SBITA - Governmental Activities","SBITA - Business-Type Activities","SBITA - Total",
    "Combined Lease+SBITA - Governmental","Combined Lease+SBITA - Business-Type","Combined Lease+SBITA - Total",
    "Lease on Gov Fund Balance Sheet?","SBITA on Gov Fund Balance Sheet?",
    "Source File","Extraction Notes"
)
for ($c = 0; $c -lt $headers.Count; $c++) {
    $ws.Cells.Item(1, $c + 1) = $headers[$c]
    $ws.Cells.Item(1, $c + 1).Font.Bold = $true
}

$row = 2
foreach ($r in ($data | Sort-Object state, fiscal_year)) {
    $ws.Cells.Item($row, 1) = $r.state
    $ws.Cells.Item($row, 2) = $r.agency
    $ws.Cells.Item($row, 3) = $r.fiscal_year
    $ws.Cells.Item($row, 4) = $r.reporting_format
    $ws.Cells.Item($row, 5) = if ($r.has_gov_wide_snp) { "Yes" } else { "No" }
    $ws.Cells.Item($row, 6) = Format-Amt $r.lease.governmental
    $ws.Cells.Item($row, 7) = Format-Amt $r.lease.business_type
    $ws.Cells.Item($row, 8) = Format-Amt $r.lease.total
    $ws.Cells.Item($row, 9) = Format-Amt $r.sbita.governmental
    $ws.Cells.Item($row, 10) = Format-Amt $r.sbita.business_type
    $ws.Cells.Item($row, 11) = Format-Amt $r.sbita.total
    $ws.Cells.Item($row, 12) = Format-Amt $r.combined_lease_sbita.governmental
    $ws.Cells.Item($row, 13) = Format-Amt $r.combined_lease_sbita.business_type
    $ws.Cells.Item($row, 14) = Format-Amt $r.combined_lease_sbita.total
    $ws.Cells.Item($row, 15) = if ($r.lease_on_gov_fund_bs) { "Yes" } else { "No" }
    $ws.Cells.Item($row, 16) = if ($r.sbita_on_gov_fund_bs) { "Yes" } else { "No" }
    $ws.Cells.Item($row, 17) = $r.source_file
    $ws.Cells.Item($row, 18) = ($r.extraction_notes -join "; ")
    $row++
}

$ws.Columns.AutoFit() | Out-Null
$wb.SaveAs($excelPath)
$wb.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null

# --- Word ---
$withData = @($data | Where-Object { $_.lease.total -or $_.sbita.total -or $_.combined_lease_sbita.total })
$govWide = @($data | Where-Object { $_.has_gov_wide_snp })
$govLease = @($data | Where-Object { $_.lease.governmental -and $_.lease.governmental -gt 0 })
$govFundLease = @($data | Where-Object { $_.lease_on_gov_fund_bs })
$govFundSbita = @($data | Where-Object { $_.sbita_on_gov_fund_bs })
$totalCount = @($data).Count

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Add()

function Add-Heading($text, $level) {
    $p = $doc.Content.Paragraphs.Add()
    $p.Range.Text = $text
    $p.Range.Font.Bold = $true
    if ($level -eq 1) { $p.Range.Font.Size = 16 } elseif ($level -eq 2) { $p.Range.Font.Size = 14 } else { $p.Range.Font.Size = 12 }
    $p.Range.InsertParagraphAfter() | Out-Null
}

function Add-Para($text) {
    $p = $doc.Content.Paragraphs.Add()
    $p.Range.Text = $text
    $p.Range.Font.Bold = $false
    $p.Range.Font.Size = 11
    $p.Range.InsertParagraphAfter() | Out-Null
}

function Add-Bullet($text) {
    $p = $doc.Content.Paragraphs.Add()
    $p.Range.Text = $text
    $p.Range.Font.Bold = $false
    $p.Range.Font.Size = 11
    $p.Range.ListFormat.ApplyBulletDefault() | Out-Null
    $p.Range.InsertParagraphAfter() | Out-Null
}

Add-Heading "Lease and SBITA Liability Reporting: Governmental Funds vs. Government-Wide Financial Statements" 1
Add-Para "Analysis of U.S. State Housing Finance Agency ACFRs - FY2024 and FY2025"
Add-Para "Prepared: July 22, 2026"
Add-Para ""

Add-Heading "1. Executive Summary" 2
Add-Para "This report addresses whether state housing finance agencies should record and report lease liabilities under GASB 87 and subscription-based information technology arrangement (SBITA) liabilities under GASB 96 on governmental fund balance sheets, or only on the government-wide Statement of Net Position."
Add-Para "Based on GASB Codification Sections 1400.101 and 1500.102 through 1500.104 (see reference extracts image001.png and image002.png in the project folder), lease and SBITA liabilities associated with governmental activities are general long-term liabilities. They should not appear on governmental fund balance sheets; they should be reported in the governmental activities column of the government-wide Statement of Net Position, and in proprietary fund statements when the underlying activity is business-type."
Add-Para ("Empirical review of " + $totalCount + " state HFA financial report files in the FY2024 and FY2025 subfolders found:")
Add-Bullet ($withData.Count.ToString() + " agency-year observations with identifiable lease, SBITA, or combined lease/SBITA liability amounts on a Statement of Net Position.")
Add-Bullet ($govWide.Count.ToString() + " agency-year observations present a government-wide Statement of Net Position with governmental and business-type activity columns.")
Add-Bullet ($govLease.Count.ToString() + " agency-year observations report lease liabilities in the governmental activities column, notably Delaware State Housing Authority.")
Add-Bullet ($govFundLease.Count.ToString() + " agency-year observations report lease liabilities on a governmental fund balance sheet.")
Add-Bullet ($govFundSbita.Count.ToString() + " agency-year observations report SBITA or subscription liabilities on a governmental fund balance sheet.")
Add-Para ""

Add-Heading "2. GASB Codification Framework" 2

Add-Heading "2.1 Section 1400.101 - Reporting Capital Assets" 3
Add-Para "GASB Codification 1400.101 requires a clear distinction between proprietary/fiduciary fund capital assets and general capital assets. Capital assets of proprietary funds are reported in both government-wide and fund financial statements. All other capital assets, including right-to-use assets arising from lessee leases and SBITA arrangements for governmental activities, should not be reported as assets in governmental funds. They should be reported in the governmental activities column of the government-wide Statement of Net Position."
Add-Para "Implication: The right-to-use asset paired with a lease or SBITA liability for governmental activities is a general capital asset. It does not belong on the governmental fund balance sheet."

Add-Heading "2.2 Section 1500.102 - Fund Liabilities" 3
Add-Para "Liabilities related to and expected to be paid from proprietary and fiduciary funds, including leases, are specific fund liabilities reported in those funds. Long-term liabilities of proprietary funds appear on both the proprietary fund Statement of Net Position and the government-wide Statement of Net Position."

Add-Heading "2.3 Section 1500.103 - General Long-Term Liabilities" 3
Add-Para "General long-term liabilities, including noncurrent lease liabilities, should not be reported as liabilities in governmental funds. They should be reported only in the governmental activities column of the government-wide Statement of Net Position. Current portions of general long-term liabilities likewise are not governmental fund liabilities; payment is typically reported as an expenditure when due."

Add-Heading "2.4 Section 1500.104 - Rationale" 3
Add-Para "GASB explains that recording general long-term debt, including lease and SBITA liabilities, on governmental fund balance sheets would be misleading because payment does not require current-period appropriation of governmental fund financial resources in the same manner as accounts payable or other current fund obligations."

Add-Heading "3. Practical Reporting Matrix" 2
Add-Para "The following matrix summarizes required presentation under GASB:"
Add-Para "Governmental activities (grant/administrative programs): Lease/SBITA liability belongs on the government-wide Statement of Net Position in the Governmental Activities column only, not on the governmental fund balance sheet. The corresponding right-of-use asset belongs on the government-wide Statement of Net Position in Governmental Activities, not on the governmental fund balance sheet."
Add-Para "Business-type activities (bond/loan programs, enterprise funds): Lease/SBITA liability belongs on the proprietary fund Statement of Net Position and on the government-wide Statement of Net Position in the Business-Type Activities column. The corresponding right-of-use asset follows the same presentation."
Add-Para "Many state HFAs are predominantly enterprise/proprietary and present a single-column Statement of Net Position. In that case, lease/SBITA amounts appear once and the Total column conceptually equals business-type activities. Agencies with both governmental and business-type columns must allocate lease/SBITA between columns based on which functions use the underlying asset."

Add-Heading "4. Empirical Findings from FY2024 and FY2025 ACFRs" 2

Add-Heading "4.1 Governmental Fund Balance Sheet" 3
Add-Para "No state HFA in the sample reported lease or SBITA liabilities on a governmental fund balance sheet, consistent with GASB 1500.103. Reconciliation schedules commonly explain that long-term liabilities, including leases, are omitted from governmental funds and included in government-wide governmental activities."

Add-Heading "4.2 Government-Wide Statement of Net Position" 3
Add-Para "Among agencies with government-wide presentation, Delaware State Housing Authority is the clearest example of lease liabilities split between columns:"
Add-Bullet "FY2024: Lease payable total 394,975 split 126,392 governmental and 268,583 business-type; Subscription payable 264,038 business-type only."
Add-Bullet "FY2025: Lease payable total 262,492 split 83,997 governmental and 178,495 business-type; Subscription payable 0."
Add-Para "Illinois Housing Development Authority FY2025 reports lease and subscription liabilities entirely in business-type activities."
Add-Para "Most other HFAs either report no lease/SBITA liability on the government-wide Statement of Net Position or report amounts only in a single enterprise column."

Add-Heading "4.3 Data Limitations" 3
Add-Para "Amounts in the companion Excel workbook were extracted automatically from text ACFR files and should be verified against official PDF statements. OCR quality varies and some agencies could not be parsed reliably. N/A indicates no amount identified on the Statement of Net Position."

Add-Heading "5. Conclusion" 2
Add-Para "Under GASB Codification 1400.101 and 1500.103 through 1500.104, lease and SBITA liabilities for governmental activities are general long-term liabilities. They should not be recorded on governmental fund balance sheets. They should be reported in the governmental activities column of the government-wide Statement of Net Position, with the related right-of-use assets reported as general capital assets in the same column."
Add-Para "For business-type housing finance programs, lease and SBITA liabilities belong on the proprietary fund Statement of Net Position and roll into the business-type activities column on the government-wide Statement of Net Position."
Add-Para "State HFAs reviewed generally follow this pattern: governmental fund balance sheets omit lease/SBITA liabilities, while enterprise or government-wide statements carry the obligations."

if (Test-Path $wordPath) { Remove-Item $wordPath -Force }
$doc.SaveAs2($wordPath)
$doc.Close()
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null

Write-Output "Excel: $excelPath"
Write-Output "Word:  $wordPath"
