param(
  [Parameter(Mandatory=$true)][string]$DocxPath,
  [Parameter(Mandatory=$true)][string]$PdfPath,
  [Parameter(Mandatory=$true)][int]$Lcid
)
$ErrorActionPreference = "Stop"
Write-Host "1: creating Word.Application"
$word = New-Object -ComObject Word.Application
$word.Visible = $true
$word.DisplayAlerts = 0
Write-Host "2: opening doc"
$doc = $word.Documents.Open($DocxPath, $false, $true)
Write-Host "3: opened"
$doc.Content.LanguageID = $Lcid
Write-Host "4: languageid set"
$rawTitle = $doc.Paragraphs.Item(1).Range.Text
$title = ($rawTitle -replace "[\r\v\n]+", " ").Trim()
Write-Host ("5: title = " + $title)
try { $doc.BuiltInDocumentProperties.Item("Title").Value = $title } catch { Write-Host ("title set failed: " + $_) }
Write-Host "6: title property set"
Write-Host "7: exporting"
$doc.ExportAsFixedFormat($PdfPath, 17, $false, 0, 0, 1, 1, 0, $true, $false, 1, $true, $true, $false)
Write-Host "8: exported"
$doc.Close(0)
Write-Host "9: closed"
$word.Quit()
Write-Host "10: quit"
