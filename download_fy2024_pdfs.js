#!/usr/bin/env node
/**
 * Download FY2024 state HFA ACFR PDFs (URL candidates derived from FY2025 direct_urls.json)
 */
const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const BASE = __dirname;
const URLS_PATH = path.join(BASE, 'FY2025', 'direct_urls.json');
const OUT_DIR = path.join(BASE, 'FY2024', 'pdf');
const LOG_PATH = path.join(BASE, 'FY2024', 'download_log.json');

const MANUAL_FY2024 = [
  { state: 'AL', abbr: 'AHFA', url: 'https://ahfa.atl1.cdn.digitaloceanspaces.com/investors/2024-ahfa-financial-statements.pdf' },
  { state: 'IL', abbr: 'IHDA', url: 'https://www.ihda.org/wp-content/uploads/2024/12/FY2024-IHDA-ACFR.pdf' },
  { state: 'DE', abbr: 'DSHA', url: 'https://auditor.delaware.gov/wp-content/uploads/sites/209/2025/04/Delaware-State-Housing-Authority-FY24-Financial-Statement-Audit-Report.pdf' },
  { state: 'WA', abbr: 'WSHFC', url: 'https://www.wshfc.org/finance/investor/AuditedFinancials2024.06.30and2023.pdf' },
  { state: 'OH', abbr: 'OHFA', url: 'https://ohiohome.org/financials/documents/FincStatementsFY24.pdf' },
  { state: 'MO', abbr: 'MHDC', url: 'https://archive.org/download/2024MHDCFinancialStatements/2024MHDCFinancialStatements.pdf' },
  { state: 'NE', abbr: 'NIFA', url: 'https://nebraskalegislature.gov/FloorDocs/108/PDF/Agencies/Nebraska_Investment_Finance_Authority/101_20241109-143146.pdf' },
  { state: 'FL', abbr: 'FloridaHousing', url: 'https://www.floridahousing.org/docs/default-source/data-docs-and-reports/finance/audited-financial-reports/2024-audited-financial-statements.pdf' },
  { state: 'MI', abbr: 'MSHDA', url: 'https://audgen.michigan.gov/wp-content/uploads/2024/10/MSHDA-ACFR-0624-AUD-Final.pdf' },
  { state: 'CO', abbr: 'CHFA', url: 'https://www.chfainfo.com/getattachment/7d8e4899-6f00-428a-80e4-f45e3ea826bd/chfa-2024-financials.pdf' },
  { state: 'CT', abbr: 'CHFA', url: 'https://www.chfa.org/assets/1/6/2024_Audited_Financial_Statement.pdf' },
  { state: 'TX', abbr: 'TDHCA', url: 'https://www.tdhca.texas.gov/sites/default/files/pdf/fa/24-BasicFinancials.pdf' },
  { state: 'NC', abbr: 'NCHFA', url: 'https://nchfa.com/sites/default/files/page_attachments/afs06-30-24.pdf' },
  { state: 'WY', abbr: 'WCDA', url: 'https://www.wyomingcda.com/wp-content/uploads/2024/12/Financial-Report-2024.pdf' },
  { state: 'WI', abbr: 'WHEDA', url: 'https://www.wheda.com/globalassets/documents/annual-reports-and-financials/2024/wheda-audit-fy-2024.pdf' },
  { state: 'WV', abbr: 'WVHDF', url: 'https://www.wvhdf.com/wp-content/uploads/2025/02/FY2024-WVHDF-Annual-Comprehensive-Financial-Report.pdf' },
  { state: 'VT', abbr: 'VHFA', url: 'https://vhfa.org/finance/statements/fy2024-vhfa-audited-financial-packagepdf' },
  { state: 'VA', abbr: 'VirginiaHousing', url: 'https://www.virginiahousing.com/-/media/docs/partners/investors/financial-statements/annual-statements/2024vhdafinancialstatements_final_public.pdf' },
  { state: 'UT', abbr: 'UtahHousing', url: 'https://www.utah.gov/pmn/files/1278910.pdf' },
  { state: 'TN', abbr: 'THDA', url: 'https://dogvxws799i6n.cloudfront.net/wp-content/uploads/THDA-Audited-Financial-Statement-6-30-2024-FINAL.pdf' },
  { state: 'SC', abbr: 'SCHFDA', url: 'https://osa.sc.gov/wp-content/uploads/2024/10/Updated-SC-Housing-Financial-Statements-FY24.pdf' },
  { state: 'PA', abbr: 'PHFA', url: 'https://www.pa.gov/content/dam/copapwp-pagov/en/budget/documents/publications-and-reports/annualfinancialreport/june-30-2024%20acfr.pdf' },
  { state: 'ND', abbr: 'NDHFA', url: 'https://www.ndhousing.nd.gov/sites/www/files/documents/Investors/AuditedFinancialStatements2024and2023.pdf' },
  { state: 'MT', abbr: 'MTHousing', url: 'https://archive.legmt.gov/content/Committees/Administration/audit/2024-25/Meetings/April-2025/24-07.pdf' },
  { state: 'MN', abbr: 'MNHousing', url: 'https://www.lrl.mn.gov/docs/2024/other/241924.pdf' },
  { state: 'ME', abbr: 'MaineHousing', url: 'https://www.mainehousing.org/docs/default-source/financial-statements/12-31-2024-audited-financials.pdf' },
  { state: 'MD', abbr: 'CDA', url: 'https://dhcd.maryland.gov/Investors/CDABondDocs/hrb2024_06_30fs.pdf' },
  { state: 'MA', abbr: 'MassHousing', url: 'https://www.masshousing.com/-/media/Files/Financials/2024-Annual-Disclosure-Report.pdf' },
  { state: 'LA', abbr: 'LHC', url: 'https://webapps3.lhc.la.gov/documents/BoardCommitteeMaterials/2025/January/ACM/LHC%20Financial%20Statement%20Audit%20Report%20for%20the%20FYE%20June%202024.pdf' },
  { state: 'KY', abbr: 'KHC', url: 'https://www.kyhousing.org/sites/default/files/2025-05/KHC%202024%20FS%20Report%20-%20Short-Form%20-%20FINAL.pdf' },
  { state: 'KS', abbr: 'KHRC', url: 'https://admin.ks.gov/browse/files/8c8b8a0deef8464faaba21b8f4e69a24/download' },
  { state: 'IN', abbr: 'IHCDA', url: 'https://www.in.gov/ihcda/files/IHCDA-2024-FY-Audited-FS.pdf' },
  { state: 'ID', abbr: 'IHFA', url: 'https://www.idahohousing.com/documents/2024-ihfa-financial-report.pdf' },
  { state: 'HI', abbr: 'HHFDC', url: 'https://files.hawaii.gov/auditor/Reports/2024_Audit/HHFDC2024.pdf' },
  { state: 'GA', abbr: 'GHFA', url: 'https://open.ga.gov/openga/report/downloadFile?rid=31838' },
  { state: 'DC', abbr: 'DCHFA', url: 'https://dchfa.org/wp-content/uploads/2025/02/final_District-of-Columbia-HFA_FS_20242025020207.pdf' },
  { state: 'AR', abbr: 'ADFA', url: 'https://adfa.arkansas.gov/wp-content/uploads/2024/12/ADFA-FS-Final-2.pdf' },
  { state: 'AK', abbr: 'AHFC', url: 'https://www.ahfc.us/download_file/view/9549/583' },
  { state: 'CA', abbr: 'CalHFA', url: 'https://www.calhfa.ca.gov/homeownership/documents/2024-ACFR.pdf' },
  { state: 'SD', abbr: 'SDHDA', url: 'https://legislativeaudit.sd.gov/reports/State/Housing%20Development%20Authority%202024.pdf' },
  { state: 'NM', abbr: 'MFA', url: 'https://housingnm.org/uploads/documents/1a_FY_2024_New_Mexico_Mortgage_Finance_Authority_Audited_Finacial_Statements.pdf' },
  { state: 'OK', abbr: 'OHFA_OK', url: 'https://www.ohfa.org/wp-content/uploads/2025/01/2024-OHFA-Single-Audit-Report-FINAL.pdf' },
];

function fy2024Candidates(url) {
  const out = new Set();
  const add = (u) => {
    if (u && u.startsWith('http')) out.add(u);
  };
  add(url);
  const transforms = [
    (u) => u.replace(/2025/g, '2024'),
    (u) => u.replace(/FY2025/gi, 'FY2024'),
    (u) => u.replace(/fy2025/gi, 'fy2024'),
    (u) => u.replace(/FY25/g, 'FY24'),
    (u) => u.replace(/0625/g, '0624'),
    (u) => u.replace(/06-30-25/gi, '06-30-24'),
    (u) => u.replace(/afs06-30-25/gi, 'afs06-30-24'),
    (u) => u.replace(/20252026/g, '20242025'),
    (u) => u.replace(/and2024\.pdf/i, 'and2023.pdf'),
    (u) => u.replace(/Financial-Report-2025/i, 'Financial-Report-2024'),
    (u) => u.replace(/25-BasicFinancials/i, '24-BasicFinancials'),
    (u) => u.replace(/2025-/g, '2024-'),
    (u) => u.replace(/FYE%20June%202025/i, 'FYE%20June%202024'),
    (u) => u.replace(/2025vhdafinancialstatements/i, '2024vhdafinancialstatements'),
    (u) => u.replace(/AuditedFinancialStatements2025and2024/i, 'AuditedFinancialStatements2024and2023'),
    (u) => u.replace(/2025MHDCFinancialStatements/i, '2024MHDCFinancialStatements'),
    (u) => u.replace(/FincStatementsFY25/i, 'FincStatementsFY24'),
    (u) => u.replace(/wheda-audit-fy-2025/i, 'wheda-audit-fy-2024'),
    (u) => u.replace(/FY2025-WVHDF/i, 'FY2024-WVHDF'),
  ];
  for (const fn of transforms) {
    try {
      add(fn(url));
    } catch (_) {
      /* ignore */
    }
  }
  return [...out];
}

function urlLooksFy2024(url) {
  const u = url.toLowerCase();
  const has2024 = /2024|fy2024|fy24|0624|06-30-24|06_30_24|and2023|24-basicfinancials|financial-report-2024|fincstatementsfy24|2024mhdc/.test(u);
  const has2025only = /2025|fy2025|fy25|0625|06-30-25|25-basicfinancials|fincstatementsfy25|2025mhdc/.test(u);
  if (has2025only && !has2024) return false;
  return has2024;
}

function fetchBuffer(url, redirects = 0) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith('https') ? https : http;
    const req = lib.get(
      url,
      {
        headers: {
          'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        },
      },
      (res) => {
        if ([301, 302, 303, 307, 308].includes(res.statusCode) && res.headers.location && redirects < 5) {
          const next = new URL(res.headers.location, url).href;
          res.resume();
          fetchBuffer(next, redirects + 1).then(resolve).catch(reject);
          return;
        }
        if (res.statusCode !== 200) {
          res.resume();
          reject(new Error(`HTTP ${res.statusCode}`));
          return;
        }
        const chunks = [];
        res.on('data', (c) => chunks.push(c));
        res.on('end', () => resolve(Buffer.concat(chunks)));
      }
    );
    req.on('error', reject);
    req.setTimeout(60000, () => req.destroy(new Error('timeout')));
  });
}

function isPdf(buf) {
  return buf.length > 5000 && buf.slice(0, 5).toString() === '%PDF-';
}

async function downloadOne(state, abbr, candidates, force = false) {
  const dest = path.join(OUT_DIR, `${state}_${abbr}_FY2024_ACFR.pdf`);
  const valid = candidates.filter(urlLooksFy2024);
  if (!valid.length) {
    return { state, downloaded: null, tried: candidates, error: 'no FY2024 URL candidates' };
  }
  if (!force && fs.existsSync(dest) && fs.statSync(dest).size > 5000) {
    return { state, downloaded: dest, skipped: true, url: null };
  }
  const tried = [];
  for (const url of valid) {
    tried.push(url);
    try {
      const buf = await fetchBuffer(url);
      if (!isPdf(buf)) continue;
      fs.writeFileSync(dest, buf);
      return { state, downloaded: dest, url, tried };
    } catch (e) {
      /* try next */
    }
  }
  return { state, downloaded: null, tried, error: 'no working URL' };
}

async function main() {
  const force = process.argv.includes('--force');
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const fy2025 = JSON.parse(fs.readFileSync(URLS_PATH, 'utf8'));
  const entries = new Map();
  for (const row of fy2025) entries.set(row.state, row);
  for (const row of MANUAL_FY2024) entries.set(row.state, row);

  const log = {};
  let ok = 0;
  for (const [state, row] of entries) {
    const manual = MANUAL_FY2024.find((m) => m.state === state);
    const candidates = manual
      ? [manual.url, ...fy2024Candidates(row.url || '').filter(urlLooksFy2024)]
      : fy2024Candidates(row.url || '').filter(urlLooksFy2024);
    const unique = [...new Set(candidates)];
    process.stdout.write(`Downloading ${state}... `);
    const result = await downloadOne(state, row.abbr, unique, force);
    log[state] = result;
    if (result.downloaded && !result.skipped) {
      ok += 1;
      console.log('OK', result.url?.slice(0, 70));
    } else if (result.skipped) {
      console.log('exists');
    } else {
      console.log('FAILED');
    }
  }

  // Keep existing root-level NE pdf
  const neRoot = path.join(BASE, 'FY2024', 'NE_NIFA_FY2024_ACFR_v2.pdf');
  if (fs.existsSync(neRoot)) {
    const dest = path.join(OUT_DIR, 'NE_NIFA_FY2024_ACFR.pdf');
    if (!fs.existsSync(dest)) fs.copyFileSync(neRoot, dest);
  }

  fs.writeFileSync(LOG_PATH, JSON.stringify(log, null, 2));
  const total = fs.readdirSync(OUT_DIR).filter((f) => f.endsWith('.pdf')).length;
  console.log(`\nDownloaded ${ok} new PDFs. FY2024/pdf now has ${total} files. Log: ${LOG_PATH}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
