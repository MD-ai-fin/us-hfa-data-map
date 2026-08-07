/**
 * Generate Excel workbook and Word report from lease_sbita_extracted_data.json
 */
const fs = require('fs');
const path = require('path');
const ExcelJS = require('exceljs');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
} = require('docx');

const BASE = path.join(__dirname);
const JSON_PATH = path.join(BASE, 'lease_sbita_extracted_data.json');
const EXCEL_PATH = path.join(BASE, 'Lease_SBITA_Liability_SN_P_by_State_FY2024_FY2025.xlsx');
const WORD_PATH = path.join(BASE, 'Lease_SBITA_Governmental_Funds_Reporting_Report.docx');

const data = JSON.parse(fs.readFileSync(JSON_PATH, 'utf8'));

function fmt(v) {
  if (v == null || v === '') return 'N/A';
  return Math.round(Number(v)).toLocaleString('en-US');
}

function amt(obj, term, col) {
  if (!obj) return 'N/A';
  const bucket = obj[term] || obj.total;
  if (!bucket) return 'N/A';
  if (col === 'gov') return fmt(bucket.governmental);
  if (col === 'biz') return fmt(bucket.business_type);
  return fmt(bucket.total);
}

function liabilityCols(prefix, obj) {
  return [
    `${prefix} Current - Gov`, `${prefix} Current - Biz`, `${prefix} Current - Total`,
    `${prefix} Noncurrent - Gov`, `${prefix} Noncurrent - Biz`, `${prefix} Noncurrent - Total`,
    `${prefix} Total - Gov`, `${prefix} Total - Biz`, `${prefix} Total - Total`,
  ].map((_, i) => {
    const terms = ['current', 'current', 'current', 'noncurrent', 'noncurrent', 'noncurrent', 'total', 'total', 'total'];
    const cols = ['gov', 'biz', 'total', 'gov', 'biz', 'total', 'gov', 'biz', 'total'];
    return amt(obj, terms[i], cols[i]);
  });
}

async function buildExcel() {
  const wb = new ExcelJS.Workbook();
  const ws = wb.addWorksheet('Lease SBITA SNP Data');

  const baseHeaders = [
    'State', 'Agency', 'Fiscal Year', 'Source Type', 'Reporting Format', 'Gov-Wide SNP?',
  ];
  const leaseHeaders = [
    'Lease Current - Governmental Activities', 'Lease Current - Business-Type Activities', 'Lease Current - Total',
    'Lease Noncurrent - Governmental Activities', 'Lease Noncurrent - Business-Type Activities', 'Lease Noncurrent - Total',
    'Lease Total - Governmental Activities', 'Lease Total - Business-Type Activities', 'Lease Total - Total',
  ];
  const sbitaHeaders = [
    'SBITA Current - Governmental Activities', 'SBITA Current - Business-Type Activities', 'SBITA Current - Total',
    'SBITA Noncurrent - Governmental Activities', 'SBITA Noncurrent - Business-Type Activities', 'SBITA Noncurrent - Total',
    'SBITA Total - Governmental Activities', 'SBITA Total - Business-Type Activities', 'SBITA Total - Total',
  ];
  const tailHeaders = [
    'Combined Total - Governmental Activities', 'Combined Total - Business-Type Activities', 'Combined Total - Total',
    'Lease on Gov Fund Balance Sheet?', 'SBITA on Gov Fund Balance Sheet?',
    'Source File', 'Extraction Notes',
  ];
  const headers = [...baseHeaders, ...leaseHeaders, ...sbitaHeaders, ...tailHeaders];

  const headerRow = ws.addRow(headers);
  headerRow.font = { bold: true };
  headerRow.alignment = { wrapText: true, vertical: 'middle' };

  const sorted = [...data].sort((a, b) => a.state.localeCompare(b.state) || a.fiscal_year.localeCompare(b.fiscal_year));

  for (const r of sorted) {
    ws.addRow([
      r.state,
      r.agency,
      r.fiscal_year,
      (r.source_type || 'txt').toUpperCase(),
      r.reporting_format,
      r.has_gov_wide_snp ? 'Yes' : 'No',
      amt(r.lease, 'current', 'gov'),
      amt(r.lease, 'current', 'biz'),
      amt(r.lease, 'current', 'total'),
      amt(r.lease, 'noncurrent', 'gov'),
      amt(r.lease, 'noncurrent', 'biz'),
      amt(r.lease, 'noncurrent', 'total'),
      amt(r.lease, 'total', 'gov'),
      amt(r.lease, 'total', 'biz'),
      amt(r.lease, 'total', 'total'),
      amt(r.sbita, 'current', 'gov'),
      amt(r.sbita, 'current', 'biz'),
      amt(r.sbita, 'current', 'total'),
      amt(r.sbita, 'noncurrent', 'gov'),
      amt(r.sbita, 'noncurrent', 'biz'),
      amt(r.sbita, 'noncurrent', 'total'),
      amt(r.sbita, 'total', 'gov'),
      amt(r.sbita, 'total', 'biz'),
      amt(r.sbita, 'total', 'total'),
      amt(r.combined_lease_sbita, 'total', 'gov'),
      amt(r.combined_lease_sbita, 'total', 'biz'),
      amt(r.combined_lease_sbita, 'total', 'total'),
      r.lease_on_gov_fund_bs ? 'Yes' : 'No',
      r.sbita_on_gov_fund_bs ? 'Yes' : 'No',
      r.source_file,
      (r.extraction_notes || []).join('; '),
    ]);
  }

  ws.columns.forEach((col) => {
    let max = 10;
    col.eachCell({ includeEmpty: false }, (cell) => {
      const len = cell.value ? String(cell.value).length : 0;
      if (len > max) max = len;
    });
    col.width = Math.min(max + 2, 40);
  });

  ws.views = [{ state: 'frozen', ySplit: 1 }];
  await wb.xlsx.writeFile(EXCEL_PATH);
}

function p(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 200 },
    bullet: opts.bullet ? { level: 0 } : undefined,
    children: [new TextRun({ text, size: opts.size || 22 })],
  });
}

function hasAnyTotal(r) {
  const check = (obj) =>
    obj?.total?.total || obj?.current?.total || obj?.noncurrent?.total;
  return check(r.lease) || check(r.sbita) || check(r.combined_lease_sbita);
}

function buildWord() {
  const withData = data.filter(hasAnyTotal);
  const withSplit = data.filter(
    (r) =>
      r.lease?.current?.total != null ||
      r.lease?.noncurrent?.total != null ||
      r.sbita?.current?.total != null ||
      r.sbita?.noncurrent?.total != null
  );
  const govWide = data.filter((r) => r.has_gov_wide_snp);
  const govLease = data.filter((r) => (r.lease?.total?.governmental || 0) > 0);
  const govFundLease = data.filter((r) => r.lease_on_gov_fund_bs);
  const govFundSbita = data.filter((r) => r.sbita_on_gov_fund_bs);

  const children = [
    new Paragraph({
      heading: HeadingLevel.TITLE,
      spacing: { after: 200 },
      children: [new TextRun({
        text: 'Lease and SBITA Liability Reporting: Governmental Funds vs. Government-Wide Financial Statements',
        bold: true,
      })],
    }),
    p('Analysis of U.S. State Housing Finance Agency ACFRs - FY2024 and FY2025'),
    p('Prepared: July 23, 2026'),
    p(''),
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('1. Executive Summary')] }),
    p('This report addresses whether state housing finance agencies should record lease and SBITA liabilities on governmental fund balance sheets or on the government-wide Statement of Net Position, and summarizes current vs noncurrent presentation in FY2024 and FY2025 ACFRs.'),
    p(`Review of ${data.length} agency-year files found ${withData.length} with identifiable liability amounts and ${withSplit.length} with separate current and noncurrent breakdowns on the Statement of Net Position.`, { bullet: true }),
    p(`${govLease.length} agency-year observations report lease liabilities in the governmental activities column.`, { bullet: true }),
    p(`${govFundLease.length} report lease liabilities on a governmental fund balance sheet; ${govFundSbita.length} report SBITA on a governmental fund balance sheet.`, { bullet: true }),
    p(''),
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('2. GASB Requirements')] }),
    p('Under GASB 1500.103, noncurrent lease and SBITA liabilities are general long-term liabilities excluded from governmental funds. Current portions are likewise not fund liabilities; payment is reported as expenditure when due. Both current and noncurrent portions belong on the government-wide Statement of Net Position (governmental and/or business-type columns).'),
    p(''),
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('3. Current vs Noncurrent Presentation')] }),
    p('Agencies typically split lease and SBITA liabilities between Current liabilities (current portion) and Noncurrent liabilities (net of current portion) on the Statement of Net Position. The companion Excel workbook groups all extracted amounts into Current, Noncurrent, and Total columns for each state and fiscal year.'),
    p('Illinois IHDA FY2025 example (amounts in thousands in source): Lease current 1,312; Lease noncurrent 564; SBITA current 532; SBITA noncurrent 781.', { bullet: true }),
    p('Montana Housing FY2025: Lease current 117,392; Lease noncurrent 2,094,576; SBITA current 76,260; SBITA noncurrent 287,397.', { bullet: true }),
    p('Ohio OHFA FY2025: Lease current 370,829; Lease noncurrent 5,643,127 (business-type/general fund column).', { bullet: true }),
    p(''),
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('4. Conclusion')] }),
    p('Lease and SBITA liabilities should not appear on governmental fund balance sheets. On the government-wide Statement of Net Position, report current and noncurrent portions in the appropriate activity columns. See Lease_SBITA_Liability_SN_P_by_State_FY2024_FY2025.xlsx for the full state-by-state data.'),
  ];

  return new Document({ sections: [{ properties: {}, children }] });
}

async function main() {
  await buildExcel();
  const doc = buildWord();
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(WORD_PATH, buffer);
  console.log('Excel:', EXCEL_PATH);
  console.log('Word:', WORD_PATH);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
