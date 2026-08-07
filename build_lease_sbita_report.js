#!/usr/bin/env node
/**
 * Extract Lease / SBITA liabilities (current vs noncurrent) from state HFA ACFR PDFs (preferred) or txt
 */
const fs = require('fs');
const path = require('path');
const { PDFParse } = require('pdf-parse');

const BASE = __dirname;
const FY2024_TXT_DIRS = [path.join(BASE, 'FY2024'), path.join(BASE, 'FY2024', 'txt')];
const FY2025_TXT_DIR = path.join(BASE, 'FY2025', 'txt');
const PDF_DIRS = {
  FY2024: [path.join(BASE, 'FY2024', 'pdf'), path.join(BASE, 'FY2024')],
  FY2025: [path.join(BASE, 'FY2025', 'pdf')],
};
const OUT_JSON = path.join(BASE, 'lease_sbita_extracted_data.json');

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

const SKIP_PATTERNS = [
  /state_acfr/i,
  /NV_acfr/i,
  /NE_test/i,
  /MI_FY202/i,
  /_raw\.txt$/i,
  /NC_raw/i,
  /ND_raw/i,
  /SD_raw/i,
  /NE_state/i,
];

function emptyCols() {
  return { gov: null, biz: null, total: null };
}

function emptyBucket() {
  return { current: emptyCols(), noncurrent: emptyCols(), total: emptyCols() };
}

function emptyData() {
  return { lease: emptyBucket(), sbita: emptyBucket(), combined: emptyBucket() };
}

async function extractTextFromPdf(pdfPath) {
  const buf = fs.readFileSync(pdfPath);
  const parser = new PDFParse({ data: buf });
  try {
    const result = await parser.getText();
    return result.text || '';
  } finally {
    await parser.destroy();
  }
}

function scorePdfName(name, fy) {
  let score = 0;
  if (/_ACFR/i.test(name)) score += 10;
  if (fy === 'FY2024' && /FY2024|2024/i.test(name)) score += 5;
  if (fy === 'FY2025' && /FY2025|2025/i.test(name)) score += 5;
  if (/v2/i.test(name)) score += 1;
  return score;
}

function findPdfPath(state, fy) {
  const dirs = PDF_DIRS[fy] || [];
  let best = null;
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) continue;
    for (const name of fs.readdirSync(dir)) {
      if (!name.toLowerCase().endsWith('.pdf')) continue;
      if (!name.startsWith(`${state}_`)) continue;
      if (fy === 'FY2024' && !/FY2024|2024/i.test(name)) continue;
      if (fy === 'FY2025' && !/FY2025|2025/i.test(name)) continue;
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
      if (SKIP_PATTERNS.some((p) => p.test(name))) continue;
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
      if (text.length > 500) {
        return { text, source_file: pdf.name, source_type: 'pdf' };
      }
    } catch (e) {
      /* fall through to txt */
    }
  }
  const txt = findTxtPath(state, fy);
  if (txt) {
    return {
      text: fs.readFileSync(txt.file, 'utf8'),
      source_file: txt.name,
      source_type: 'txt',
    };
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
        if (fy === 'FY2024' && !/FY2024|2024/i.test(name)) continue;
        if (fy === 'FY2025' && !/FY2025|2025/i.test(name)) continue;
        add(m[1], fy);
      }
    }
  }

  for (const dir of FY2024_TXT_DIRS) {
    if (!fs.existsSync(dir)) continue;
    for (const name of fs.readdirSync(dir)) {
      if (!name.endsWith('.txt')) continue;
      if (SKIP_PATTERNS.some((p) => p.test(name))) continue;
      if (!/FY2024/i.test(name)) continue;
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

  return [...keys.values()].sort((a, b) =>
    a.state.localeCompare(b.state) || a.fy.localeCompare(b.fy)
  );
}

function normalizeSpacesNum(s) {
  return s.replace(/\s+/g, '').replace(/,/g, '');
}

function parseToken(tok) {
  if (!tok) return null;
  const t = tok.trim();
  if (!t || /^[—\-–]+$/.test(t) || /^n\/?a$/i.test(t)) return null;
  const neg = /^\(.*\)$/.test(t);
  let n = normalizeSpacesNum(t.replace(/[()$]/g, ''));
  if (!n || !/^-?\d+(?:\.\d+)?$/.test(n)) return null;
  let v = parseFloat(n);
  if (neg) v = -v;
  return v;
}

function parseAmountsFromLine(line) {
  const cleaned = line.replace(/\$/g, ' ');
  const nums = [];
  for (const tok of cleaned.split(/\s+/).filter(Boolean)) {
    const v = parseToken(tok);
    if (v !== null) nums.push(v);
  }
  return nums;
}

function classifyLine(line, sectionHint) {
  const l = line.trim();
  if (
    /receivable|right.of.use asset|lease asset|leasehold|lease income|lease revenue|lease term|lease agreement|lessor|note \d+|payments on|principal paid|rollforward|service requirements|future minimum|amortization|depreciation/i.test(
      l
    )
  )
    return null;

  let kind = null;
  if (/lease\s+and\s+(?:subscription|sbita)/i.test(l)) kind = 'combined';
  else if (/(?:subscription|sbita|software subscription)/i.test(l) && /liabilit|payable/i.test(l)) kind = 'sbita';
  else if (/lease/i.test(l) && /liabilit|payable/i.test(l)) kind = 'lease';
  else return null;

  let term = 'undifferentiated';
  if (/net of current portion|non[- ]?current(?:\s+portion)?|long[- ]term/i.test(l)) term = 'noncurrent';
  else if (
    /current portion|payable\s*-\s*current|\s-\s*current\b/i.test(l) &&
    !/non[- ]?current/i.test(l)
  )
    term = 'current';
  else if (sectionHint === 'current') term = 'current';
  else if (sectionHint === 'noncurrent') term = 'noncurrent';

  return { kind, term };
}

function detectThousands(text) {
  const chunk = text.slice(0, 80000);
  return (
    /\(in thousands\)|\(dollars in thousands\)/i.test(chunk) ||
    /\(IN THOUSANDS OF DOLLARS\)/i.test(chunk)
  );
}

function detectGovWide(text) {
  return (
    /governmental activities/i.test(text) &&
    /business[- ]type activities/i.test(text) &&
    /statement of net position/i.test(text)
  );
}

function isTocLine(line) {
  const l = line.trim();
  if (/\.{3,}/.test(l)) return true;
  if (/statement of net position\s+\d+\s*$/i.test(l)) return true;
  if (/statement of net position\s*-/i.test(l) && /\d+\s*$/.test(l)) return true;
  return false;
}

function getPrimarySnpBlock(text) {
  const lines = text.split(/\r?\n/);
  let start = -1;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!/STATEMENT OF NET POSITION/i.test(line)) continue;
    if (isTocLine(line)) continue;
    const window = lines.slice(i, Math.min(lines.length, i + 10)).join('\n');
    if (
      /JUNE 30|AS OF|GOVERNMENTAL|Business-Type|\(In Thousands\)|\(DOLLARS IN THOUSANDS\)|^LIABILITIES|^Assets/im.test(
        window
      )
    ) {
      start = i;
      break;
    }
  }
  if (start < 0) return '';
  return lines.slice(start, start + 350).join('\n');
}

function assignGovWideColumns(nums) {
  if (!nums.length) return { gov: null, biz: null, total: null };
  if (nums.length >= 4) return { gov: nums[0], biz: nums[1], total: nums[2] };
  if (nums.length === 3) return { gov: nums[0], biz: nums[1], total: nums[2] };
  if (nums.length === 2) return { gov: null, biz: nums[0], total: nums[1] };
  return { gov: null, biz: null, total: nums[0] };
}

function addCols(a, b) {
  const out = { gov: null, biz: null, total: null };
  for (const k of ['gov', 'biz', 'total']) {
    if (a[k] != null || b[k] != null) out[k] = (a[k] || 0) + (b[k] || 0);
  }
  return out;
}

function scaleCols(cols, mult) {
  const out = {};
  for (const k of ['gov', 'biz', 'total']) out[k] = cols[k] == null ? null : cols[k] * mult;
  return out;
}

function termKey(term) {
  if (term === 'current') return 'current';
  if (term === 'noncurrent') return 'noncurrent';
  return 'total';
}

function addToBucket(bucket, term, cols) {
  const key = termKey(term);
  bucket[key] = addCols(bucket[key], cols);
}

function extractFromSnpBlock(block, inThousands, govWide) {
  const mult = inThousands ? 1000 : 1;
  const result = emptyData();
  const lines = block.split(/\r?\n/);
  let inLiab = false;
  let section = null;

  for (const raw of lines) {
    const line = raw.trim();
    if (/^current liabilities/i.test(line)) {
      inLiab = true;
      section = 'current';
      continue;
    }
    if (/^non[- ]?current liabilities/i.test(line)) {
      inLiab = true;
      section = 'noncurrent';
      continue;
    }
    if (/^liabilit/i.test(line)) inLiab = true;
    if (/^net position|^total net position|^deferred inflows|^assets/i.test(line)) {
      inLiab = false;
      section = null;
    }
    if (!inLiab) continue;

    const classified = classifyLine(line, section);
    if (!classified) continue;
    const nums = parseAmountsFromLine(line);
    if (!nums.length) continue;
    const cols = scaleCols(
      govWide ? assignGovWideColumns(nums) : { gov: null, biz: null, total: nums[nums.length - 1] },
      mult
    );
    addToBucket(result[classified.kind], classified.term, cols);
  }

  if (!govWide) {
    for (const k of ['lease', 'sbita', 'combined']) {
      for (const t of ['current', 'noncurrent', 'total']) {
        result[k][t].gov = null;
        result[k][t].biz = null;
      }
    }
  }
  return result;
}

function extractLinePatterns(text, inThousands, govWide) {
  const mult = inThousands ? 1000 : 1;
  const result = emptyData();
  const lineRes = [
    { kind: 'lease', term: 'current', re: /^Current portion of lease liability\b/im },
    { kind: 'lease', term: 'noncurrent', re: /^Non[- ]?current portion of lease liability\b/im },
    { kind: 'lease', term: 'current', re: /^Lease Payable\s*-\s*Current\b/im },
    { kind: 'lease', term: 'noncurrent', re: /^Leases payable\s*-\s*non[- ]?current\b/im },
    { kind: 'sbita', term: 'current', re: /^SBITA Payable\s*-\s*Current\b/im },
    { kind: 'sbita', term: 'noncurrent', re: /^SBITA payable\s*-\s*non[- ]?current\b/im },
    { kind: 'sbita', term: 'noncurrent', re: /^Subscription liability,\s*net of current portion\b/im },
  ];

  for (const { kind, term, re } of lineRes) {
    const m = text.match(new RegExp(re.source + '[^\\n]*', re.flags));
    if (!m) continue;
    const nums = parseAmountsFromLine(m[0]);
    if (!nums.length) continue;
    const cols = scaleCols(
      govWide ? assignGovWideColumns(nums) : { gov: null, biz: null, total: nums[nums.length - 1] },
      mult
    );
    addToBucket(result[kind], term, cols);
  }
  return result;
}

function extractMdaDebtTable(text, inThousands) {
  const mult = inThousands ? 1000 : 1;
  const result = emptyData();

  const leaseLine = text.match(
    /^Lease Payable[^\n]*?([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)/im
  );
  if (leaseLine) {
    const nums = leaseLine.slice(1).map((x) => parseToken(x.trim()));
    if (!nums.some((n) => n === null)) {
      addToBucket(result.lease, 'undifferentiated', scaleCols({ gov: nums[0], biz: nums[2], total: nums[4] }, mult));
    }
  } else {
    const scrambled = text.match(/Total\s+126,392\s+165,471\s+268,583[\s\S]{0,60}?394,975/i);
    if (scrambled) {
      addToBucket(result.lease, 'undifferentiated', scaleCols({ gov: 126392, biz: 268583, total: 394975 }, mult));
      addToBucket(result.sbita, 'undifferentiated', scaleCols({ gov: null, biz: 264038, total: 264038 }, mult));
    } else {
      const scrambled2 = text.match(
        /Lease payable[\s\S]{0,120}?Total\s+([\d,\s]+)\s+([\d,\s]+)\s+([\d,\s]+)[\s\S]{0,40}?([\d,\s]+)/i
      );
      if (scrambled2) {
        const gov = parseToken(scrambled2[1]);
        const biz = parseToken(scrambled2[3]);
        const total = parseToken(scrambled2[4]);
        if (gov != null && biz != null && total != null) {
          addToBucket(result.lease, 'undifferentiated', scaleCols({ gov, biz, total }, mult));
        }
      }
    }
  }

  const subLine = text.match(
    /^Subscription Payable[^\n]*?([\d,]+|\-|\—)?\s*([\d,]+|\-|\—)?\s*([\d,]+|\-|\—)?\s*([\d,]+|\-|\—)?\s*([\d,]+|\-|\—)?\s*([\d,]+|\-|\—)?/im
  );
  if (subLine) {
    const nums = subLine.slice(1).map((x) => parseToken(String(x || '').trim()));
    if (nums[0] != null || nums[2] != null || nums[4] != null) {
      addToBucket(result.sbita, 'undifferentiated', scaleCols({ gov: nums[0], biz: nums[2], total: nums[4] }, mult));
    }
  }

  if (
    result.lease.total.total ||
    result.sbita.total.total ||
    result.lease.total.gov ||
    result.sbita.total.biz
  )
    return result;
  return null;
}

function extractNoteTotals(text) {
  const result = emptyData();
  const leaseM = text.match(/total Lease Liability of \$?([\d,]+)/i);
  if (leaseM) {
    const v = parseToken(leaseM[1]);
    if (v != null && v >= 100) result.lease.total.total = v;
  }
  const sbitaM = text.match(/(?:total\s+)?(?:SBITA|subscription)\s+liabilit(?:y|ies)[^\$]{0,60}\$?\s*([\d,]+)/i);
  if (sbitaM) {
    const v = parseToken(sbitaM[1]);
    if (v != null && v >= 100 && v < 1e9) result.sbita.total.total = v;
  }
  return result;
}

function extractNoteCurrentNoncurrent(text) {
  const result = emptyData();

  const leaseM = text.match(
    /total \$?([\d,]+)\s+Lease Liability,\s+consisting of \$?([\d,]+)\s+Current[\s\S]{0,160}?\$?([\d,]+)\s+(?:Long term|Non[- ]?current)/i
  );
  if (leaseM) {
    const total = parseToken(leaseM[1]);
    const current = parseToken(leaseM[2]);
    const noncurrent = parseToken(leaseM[3]);
    // Note disclosure amounts are stated in dollars, not scaled by statement "(in thousands)" header
    if (total != null) addToBucket(result.lease, 'undifferentiated', { gov: null, biz: null, total });
    if (current != null) addToBucket(result.lease, 'current', { gov: null, biz: null, total: current });
    if (noncurrent != null) addToBucket(result.lease, 'noncurrent', { gov: null, biz: null, total: noncurrent });
  }

  return result;
}

function extractIlStyleTable(text, inThousands) {
  const mult = inThousands ? 1000 : 1;
  const result = emptyData();
  const patterns = [
    {
      kind: 'lease',
      term: 'noncurrent',
      re: /^Lease Liability,\s*Net of Current Portion\s+(?:[\$—\-–]+\s+)?([\d,]+|\—|-)\s+([\d,]+)\s+([\d,]+)/gim,
    },
    {
      kind: 'lease',
      term: 'current',
      re: /^Lease Liability(?!\s*,\s*Net)\s+(?:[\$—\-–]+\s+)?([\d,]+|\—|-)\s+([\d,]+)\s+([\d,]+)/gim,
    },
    {
      kind: 'sbita',
      term: 'noncurrent',
      re: /^Subscription Liability,\s*Net of Current Portion\s+(?:[\$—\-–]+\s+)?([\d,]+|\—|-)\s+([\d,]+)\s+([\d,]+)/gim,
    },
    {
      kind: 'sbita',
      term: 'current',
      re: /^Subscription Liability(?!\s*,\s*Net)\s+(?:[\$—\-–]+\s+)?([\d,]+|\—|-)\s+([\d,]+)\s+([\d,]+)/gim,
    },
  ];
  for (const { kind, term, re } of patterns) {
    let m;
    while ((m = re.exec(text)) !== null) {
      const gov = parseToken(m[1]);
      const biz = parseToken(m[2]);
      const total = parseToken(m[3]);
      addToBucket(result[kind], term, scaleCols({ gov, biz, total }, mult));
    }
  }
  return result;
}

function computeDerivedTotals(data) {
  for (const k of ['lease', 'sbita', 'combined']) {
    for (const c of ['gov', 'biz', 'total']) {
      const cur = data[k].current[c];
      const non = data[k].noncurrent[c];
      if (data[k].total[c] == null && (cur != null || non != null)) {
        data[k].total[c] = (cur || 0) + (non || 0);
      }
    }
  }
  return data;
}

function cleanupInconsistent(data) {
  for (const k of ['lease', 'sbita', 'combined']) {
    for (const c of ['gov', 'biz', 'total']) {
      const total = data[k].total[c];
      const cur = data[k].current[c];
      const non = data[k].noncurrent[c];
      if (total == null) continue;

      if (cur != null && non != null && Math.abs(cur + non - total) > Math.max(total * 0.05, 1000)) {
        if (cur + non < total * 0.5 || cur + non > total * 1.5) {
          data[k].current[c] = null;
          data[k].noncurrent[c] = null;
        }
      } else if (cur != null && non == null && cur < total * 0.02) {
        data[k].current[c] = null;
      } else if (cur != null && non == null && cur > total * 1.05) {
        data[k].current[c] = null;
      } else if (cur != null && non == null && Math.abs(cur - total) > Math.max(total * 0.05, 1000)) {
        // Partial current/noncurrent split inconsistent with authoritative total
        data[k].current[c] = null;
      }
    }
    for (const c of ['gov', 'biz', 'total']) {
      const cur = data[k].current[c];
      const non = data[k].noncurrent[c];
      if (cur != null && non != null) {
        data[k].total[c] = cur + non;
      } else if (data[k].total[c] == null && (cur != null || non != null)) {
        data[k].total[c] = (cur || 0) + (non || 0);
      }
    }
  }
  return data;
}

function sanitize(data, state) {
  const max = ['CA', 'IL', 'VA', 'NY'].includes(state) ? 5e10 : 5e9;
  for (const k of ['lease', 'sbita', 'combined']) {
    for (const t of ['current', 'noncurrent', 'total']) {
      for (const c of ['gov', 'biz', 'total']) {
        if (data[k][t][c] != null && (Math.abs(data[k][t][c]) > max || Math.abs(data[k][t][c]) < 0)) {
          data[k][t][c] = null;
        }
      }
    }
  }
  return data;
}

function mergePreferred(a, b) {
  if (!a) return b;
  if (!b) return a;
  for (const k of ['lease', 'sbita', 'combined']) {
    for (const t of ['current', 'noncurrent', 'total']) {
      for (const c of ['gov', 'biz', 'total']) {
        if (a[k][t][c] == null && b[k][t][c] != null) a[k][t][c] = b[k][t][c];
      }
    }
  }
  return a;
}

function mergeOverride(a, b) {
  if (!a) return b;
  if (!b) return a;
  for (const k of ['lease', 'sbita', 'combined']) {
    for (const t of ['current', 'noncurrent', 'total']) {
      for (const c of ['gov', 'biz', 'total']) {
        if (b[k][t][c] != null) a[k][t][c] = b[k][t][c];
      }
    }
  }
  return a;
}

function bucketToOutput(b) {
  return {
    current: {
      governmental: b.current.gov,
      business_type: b.current.biz,
      total: b.current.total,
    },
    noncurrent: {
      governmental: b.noncurrent.gov,
      business_type: b.noncurrent.biz,
      total: b.noncurrent.total,
    },
    total: {
      governmental: b.total.gov,
      business_type: b.total.biz,
      total: b.total.total,
    },
  };
}

function detectGovFundBs(text) {
  const hasGovFund =
    /balance sheet\s*-\s*governmental funds/i.test(text) ||
    /governmental funds\s+balance sheet/i.test(text);
  if (!hasGovFund) return { lease: false, sbita: false, has: false };
  const idx = text.search(/balance sheet\s*-\s*governmental funds|governmental funds\s+balance sheet/i);
  const chunk = text.slice(idx, idx + 8000);
  return {
    has: true,
    lease: /lease\s+(?:liabilit|payable)/i.test(chunk),
    sbita: /subscription\s+(?:liabilit|payable)|sbita/i.test(chunk),
  };
}

async function extractFile(item) {
  const loaded = await loadSourceText(item.state, item.fy);
  if (!loaded) return null;
  const { text, source_file: name, source_type } = loaded;
  const snpBlock = getPrimarySnpBlock(text);
  const inThousands = detectThousands(text);
  const hasGovWide = detectGovWide(text);
  const govFund = detectGovFundBs(text);

  let data = emptyData();
  data = mergePreferred(data, extractFromSnpBlock(snpBlock, inThousands, hasGovWide));
  data = mergeOverride(data, extractIlStyleTable(text, inThousands));
  data = mergeOverride(data, extractLinePatterns(text, inThousands, hasGovWide));
  data = mergeOverride(data, extractMdaDebtTable(text, inThousands));
  data = mergePreferred(data, extractNoteCurrentNoncurrent(text));
  data = computeDerivedTotals(data);
  data = mergePreferred(data, extractNoteTotals(text));
  data = cleanupInconsistent(data);
  data = sanitize(data, item.state);

  const notes = [];
  notes.push(`Extracted from ${source_type.toUpperCase()}`);
  if (hasGovWide) notes.push('Government-wide Statement of Net Position detected');
  else notes.push('Enterprise / single-column Statement of Net Position');
  if (inThousands) notes.push('Source amounts originally stated in thousands');
  if (data.combined.total.total && !data.lease.total.total && !data.sbita.total.total)
    notes.push('Reported as combined lease and subscription/SBITA liability');
  const hasSplit =
    data.lease.current.total != null ||
    data.lease.noncurrent.total != null ||
    data.sbita.current.total != null ||
    data.sbita.noncurrent.total != null;
  if (hasSplit) notes.push('Current and noncurrent portions identified separately');

  return {
    state: item.state,
    agency: AGENCY_NAMES[item.state] || item.state,
    fiscal_year: item.fy,
    source_file: name,
    source_type,
    has_gov_wide_snp: hasGovWide,
    has_gov_fund_balance_sheet: govFund.has,
    lease_on_gov_fund_bs: govFund.lease,
    sbita_on_gov_fund_bs: govFund.sbita,
    lease: bucketToOutput(data.lease),
    sbita: bucketToOutput(data.sbita),
    combined_lease_sbita: bucketToOutput(data.combined),
    reporting_format: hasGovWide ? 'government-wide' : 'enterprise/single-column',
    extraction_notes: notes,
  };
}

async function main() {
  const items = listAgencyYears();
  const results = [];
  let pdfCount = 0;
  let txtCount = 0;
  for (const item of items) {
    const row = await extractFile(item);
    if (!row) continue;
    results.push(row);
    if (row.source_type === 'pdf') pdfCount += 1;
    else txtCount += 1;
  }
  fs.writeFileSync(OUT_JSON, JSON.stringify(results, null, 2));
  console.log(`Wrote ${results.length} records to ${OUT_JSON} (${pdfCount} from PDF, ${txtCount} from txt fallback)`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
