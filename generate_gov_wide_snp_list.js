#!/usr/bin/env node
/**
 * Excel list: state HFAs with governmental + business-type columns on gov-wide Statement of Net Position
 */
const fs = require('fs');
const path = require('path');
const ExcelJS = require('exceljs');
const { PDFParse } = require('pdf-parse');

const BASE = __dirname;
const OUT_PATH = path.join(BASE, 'Gov_Wide_SNP_Dual_Column_Agencies.xlsx');

const FY2024_TXT_DIRS = [path.join(BASE, 'FY2024'), path.join(BASE, 'FY2024', 'txt')];
const FY2025_TXT_DIR = path.join(BASE, 'FY2025', 'txt');
const PDF_DIRS = {
  FY2024: [path.join(BASE, 'FY2024', 'pdf'), path.join(BASE, 'FY2024')],
  FY2025: [path.join(BASE, 'FY2025', 'pdf')],
};

const AGENCY_NAMES = {
  AK: 'Alaska Housing Finance Corporation',
  AL: 'Alabama Housing Finance Authority',
  AR: 'Arkansas Development Finance Authority',
  AZ: 'Arizona Department of Housing',
  CA: 'California Housing Finance Agency',
  CO: 'Colorado Housing and Finance Authority',
  CT: 'Connecticut Housing Finance Authority',
  DC: 'District of Columbia Housing Finance Agency',
  DE: 'Delaware State Housing Authority',
  FL: 'Florida Housing Finance Corporation',
  GA: 'Georgia Housing Finance Authority',
  HI: 'Hawaii Housing Finance and Development Corporation',
  IA: 'Iowa Finance Authority',
  ID: 'Idaho Housing and Finance Association',
  IL: 'Illinois Housing Development Authority',
  IN: 'Indiana Housing and Community Development Authority',
  KS: 'Kansas Housing Resources Corporation',
  KY: 'Kentucky Housing Corporation',
  LA: 'Louisiana Housing Corporation',
  MA: 'Massachusetts Housing Finance Agency',
  MD: 'Maryland Community Development Administration',
  ME: 'Maine State Housing Authority',
  MI: 'Michigan State Housing Development Authority',
  MN: 'Minnesota Housing Finance Agency',
  MO: 'Missouri Housing Development Commission',
  MS: 'Mississippi Home Corporation',
  MT: 'Montana Housing',
  NC: 'North Carolina Housing Finance Agency',
  ND: 'North Dakota Housing Finance Agency',
  NE: 'Nebraska Investment Finance Authority',
  NH: 'New Hampshire Housing Finance Authority',
  NJ: 'New Jersey Housing and Mortgage Finance Agency',
  NM: 'New Mexico Mortgage Finance Authority',
  NV: 'Nevada Housing Division',
  OH: 'Ohio Housing Finance Agency',
  OK: 'Oklahoma Housing Finance Agency',
  PA: 'Pennsylvania Housing Finance Agency',
  SC: 'South Carolina State Housing Finance and Development Authority',
  SD: 'South Dakota Housing Development Authority',
  TN: 'Tennessee Housing Development Agency',
  TX: 'Texas Department of Housing and Community Affairs',
  UT: 'Utah Housing Corporation',
  VA: 'Virginia Housing',
  VT: 'Vermont Housing Finance Agency',
  WA: 'Washington State Housing Finance Commission',
  WI: 'Wisconsin Housing and Economic Development Authority',
  WV: 'West Virginia Housing Development Fund',
  WY: 'Wyoming Community Development Authority',
};

const SKIP_TXT = [/state_acfr/i, /NV_acfr/i, /NE_test/i, /MI_FY202/i, /_raw\.txt$/i, /NC_raw/i, /ND_raw/i, /SD_raw/i, /NE_state/i];

async function extractTextFromPdf(pdfPath) {
  const parser = new PDFParse({ data: fs.readFileSync(pdfPath) });
  try {
    return (await parser.getText()).text || '';
  } finally {
    await parser.destroy();
  }
}

function scorePdfName(name, fy) {
  let score = 0;
  if (/_ACFR/i.test(name)) score += 10;
  if (fy === 'FY2024' && /FY2024|2024/i.test(name) && !/FY2025|_FY2025/i.test(name)) score += 5;
  if (fy === 'FY2025' && /FY2025|2025/i.test(name) && !/FY2024|_FY2024/i.test(name)) score += 5;
  return score;
}

function findPdfPath(state, fy) {
  let best = null;
  for (const dir of PDF_DIRS[fy] || []) {
    if (!fs.existsSync(dir)) continue;
    for (const name of fs.readdirSync(dir)) {
      if (!name.toLowerCase().endsWith('.pdf')) continue;
      if (!name.startsWith(`${state}_`)) continue;
      if (fy === 'FY2024' && (/FY2025|_FY2025/i.test(name) || !/FY2024|2024/i.test(name))) continue;
      if (fy === 'FY2025' && (/FY2024|_FY2024/i.test(name) || !/FY2025|2025/i.test(name))) continue;
      const full = path.join(dir, name);
      if (fs.statSync(full).size < 5000) continue;
      const score = scorePdfName(name, fy);
      if (!best || score > best.score) best = { file: full, name, score };
    }
  }
  return best;
}

function findTxtPath(state, fy) {
  const dirs = fy === 'FY2024' ? FY2024_TXT_DIRS : [FY2025_TXT_DIR];
  let best = null;
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) continue;
    for (const name of fs.readdirSync(dir)) {
      if (!name.endsWith('.txt')) continue;
      if (SKIP_TXT.some((p) => p.test(name))) continue;
      if (!name.startsWith(`${state}_`)) continue;
      if (fy === 'FY2024' && !/FY2024/i.test(name)) continue;
      if (fy === 'FY2025' && !/FY2025/i.test(name)) continue;
      const full = path.join(dir, name);
      const score = (/_ACFR\.txt$/i.test(name) ? 10 : 0) + (!/_raw/i.test(name) ? 5 : 0);
      if (!best || score > best.score) best = { file: full, name, score };
    }
  }
  return best;
}

async function loadSourceText(state, fy) {
  const pdf = findPdfPath(state, fy);
  if (pdf) {
    try {
      const text = await extractTextFromPdf(pdf.file);
      if (text.length > 500) return { text, source_file: pdf.name, source_type: 'PDF' };
    } catch (_) {
      /* fallback */
    }
  }
  const txt = findTxtPath(state, fy);
  if (txt) {
    return { text: fs.readFileSync(txt.file, 'utf8'), source_file: txt.name, source_type: 'TXT' };
  }
  return null;
}

function listAgencyYears() {
  const keys = new Map();
  const add = (state, fy) => keys.set(`${state}_${fy}`, { state, fy });
  for (const fy of ['FY2024', 'FY2025']) {
    for (const dir of PDF_DIRS[fy] || []) {
      if (!fs.existsSync(dir)) continue;
      for (const name of fs.readdirSync(dir)) {
        if (!name.toLowerCase().endsWith('.pdf')) continue;
        const m = name.match(/^([A-Z]{2})_/);
        if (!m) continue;
        if (fy === 'FY2024' && (/FY2025|_FY2025/i.test(name) || !/FY2024|2024/i.test(name))) continue;
        if (fy === 'FY2025' && (/FY2024|_FY2024/i.test(name) || !/FY2025|2025/i.test(name))) continue;
        add(m[1], fy);
      }
    }
  }
  for (const dir of FY2024_TXT_DIRS) {
    if (!fs.existsSync(dir)) continue;
    for (const name of fs.readdirSync(dir)) {
      if (!name.endsWith('.txt') || SKIP_TXT.some((p) => p.test(name)) || !/FY2024/i.test(name)) continue;
      const m = name.match(/^([A-Z]{2})_/);
      if (m) add(m[1], 'FY2024');
    }
  }
  if (fs.existsSync(FY2025_TXT_DIR)) {
    for (const name of fs.readdirSync(FY2025_TXT_DIR)) {
      if (!name.endsWith('.txt')) continue;
      const m = name.match(/^([A-Z]{2})_/);
      if (m) add(m[1], 'FY2025');
    }
  }
  return [...keys.values()].sort((a, b) => a.state.localeCompare(b.state) || a.fy.localeCompare(b.fy));
}

function hasDualColumnGovWideSnp(text) {
  if (!/statement of net position/i.test(text)) return false;
  const hasGov =
    /governmental activities/i.test(text) ||
    /governmental activity/i.test(text) ||
    /GOVERNMENTAL\s+BUSINESS[- ]TYPE/i.test(text);
  const hasBiz =
    /business[- ]type activities/i.test(text) ||
    /business type activities/i.test(text) ||
    /GOVERNMENTAL\s+BUSINESS[- ]TYPE/i.test(text);
  return hasGov && hasBiz;
}

async function main() {
  const items = listAgencyYears();
  const matches = [];

  for (const item of items) {
    const loaded = await loadSourceText(item.state, item.fy);
    if (!loaded) continue;
    if (!hasDualColumnGovWideSnp(loaded.text)) continue;
    matches.push({
      state: item.state,
      agency: AGENCY_NAMES[item.state] || item.state,
      fiscal_year: item.fy,
      source_type: loaded.source_type,
      source_file: loaded.source_file,
      dual_column_gov_wide_snp: 'Yes',
    });
  }

  const wb = new ExcelJS.Workbook();

  const detail = wb.addWorksheet('Agency-Year Detail');
  const headers = [
    'State', 'Agency', 'Fiscal Year', 'Dual-Column Gov-Wide SNP?',
    'Source Type', 'Source File',
  ];
  detail.addRow(headers).font = { bold: true };
  for (const r of matches) {
    detail.addRow([
      r.state, r.agency, r.fiscal_year, r.dual_column_gov_wide_snp,
      r.source_type, r.source_file,
    ]);
  }

  const byState = new Map();
  for (const r of matches) {
    if (!byState.has(r.state)) {
      byState.set(r.state, {
        state: r.state,
        agency: r.agency,
        fy2024: 'No',
        fy2025: 'No',
      });
    }
    const row = byState.get(r.state);
    if (r.fiscal_year === 'FY2024') row.fy2024 = 'Yes';
    if (r.fiscal_year === 'FY2025') row.fy2025 = 'Yes';
  }

  const summary = wb.addWorksheet('By State Summary');
  summary.addRow([
    'State', 'Agency', 'FY2024 Dual-Column Gov-Wide SNP?', 'FY2025 Dual-Column Gov-Wide SNP?',
  ]).font = { bold: true };
  for (const r of [...byState.values()].sort((a, b) => a.state.localeCompare(b.state))) {
    summary.addRow([r.state, r.agency, r.fy2024, r.fy2025]);
  }

  for (const ws of [detail, summary]) {
    ws.columns.forEach((col) => {
      let max = 12;
      col.eachCell({ includeEmpty: false }, (cell) => {
        const len = cell.value ? String(cell.value).length : 0;
        if (len > max) max = len;
      });
      col.width = Math.min(max + 2, 55);
    });
    ws.views = [{ state: 'frozen', ySplit: 1 }];
  }

  await wb.xlsx.writeFile(OUT_PATH);
  console.log(`Wrote ${matches.length} agency-year rows (${byState.size} states) to ${OUT_PATH}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
