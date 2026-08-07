/**
 * Rebuild docs/hfa_report_links.json with corrected agency pages and PDF links.
 * Dead/404 PDF links are cleared rather than left pointing to broken URLs.
 */
const fs = require("fs");
const path = require("path");
const https = require("https");
const http = require("http");

process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

const catalog = JSON.parse(fs.readFileSync("FY2025/state_hfa_catalog.json", "utf8"));
const direct = JSON.parse(fs.readFileSync("FY2025/direct_urls.json", "utf8"));
const log24 = JSON.parse(fs.readFileSync("FY2024/download_log.json", "utf8"));
const log25 = JSON.parse(fs.readFileSync("FY2025/download_log.json", "utf8"));

// Manual FY2024 list aligned with download_fy2024_pdfs.js (with MassHousing path corrected)
const MANUAL_FY2024 = [
  { state: "AL", url: "https://ahfa.atl1.cdn.digitaloceanspaces.com/investors/2024-ahfa-financial-statements.pdf" },
  { state: "IL", url: "https://www.ihda.org/wp-content/uploads/2024/12/IHDA-June-30-2024-ACFR-1.pdf" },
  { state: "DE", url: "https://auditor.delaware.gov/wp-content/uploads/sites/209/2025/04/Delaware-State-Housing-Authority-FY24-Financial-Statement-Audit-Report.pdf" },
  { state: "WA", url: "https://www.wshfc.org/finance/investor/AuditedFinancials2024.06.30and2023.pdf" },
  { state: "OH", url: "https://ohiohome.org/financials/documents/FincStatementsFY24.pdf" },
  { state: "MO", url: "https://archive.org/download/2024MHDCFinancialStatements/2024MHDCFinancialStatements.pdf" },
  { state: "NE", url: "https://nebraskalegislature.gov/FloorDocs/108/PDF/Agencies/Nebraska_Investment_Finance_Authority/101_20241109-143146.pdf" },
  { state: "FL", url: "https://www.floridahousing.org/docs/default-source/data-docs-and-reports/finance/audited-financial-reports/2024-audited-financial-statements.pdf" },
  { state: "MI", url: "https://audgen.michigan.gov/wp-content/uploads/2024/10/MSHDA-ACFR-0624-AUD-Final.pdf" },
  { state: "CO", url: "https://www.chfainfo.com/getattachment/73478f64-62be-4dbc-a9c7-137f09539fd2/chfa-2024-financials.pdf" },
  { state: "CT", url: "https://www.chfa.org/assets/1/6/2024_Annual_Audited_Financial_Statement.pdf" },
  { state: "TX", url: "https://www.tdhca.texas.gov/sites/default/files/pdf/fa/24-BasicFinancials.pdf" },
  { state: "NC", url: "https://nchfa.com/sites/default/files/page_attachments/afs06-30-24.pdf" },
  { state: "WY", url: "https://www.wyomingcda.com/wp-content/uploads/2024/12/Financial-Report-2024.pdf" },
  { state: "WI", url: "https://www.wheda.com/globalassets/documents/annual-reports-and-financials/2024/wheda-audit-fy-2024.pdf" },
  { state: "WV", url: "https://www.wvhdf.com/wp-content/uploads/2025/02/FY2024-WVHDF-Annual-Comprehensive-Financial-Report.pdf" },
  { state: "VT", url: "https://vhfa.org/finance/statements/fy2024-audited-financial-statements-final-w-opinionpdf" },
  {
    state: "VA",
    url: "https://mc-7eaf08cc-3802-4bab-9abf-a732-cdn-endpoint.azureedge.net/-/media/docs/partners/investors/financial-statements/annual-statements/2024vhdafinancialstatements_final.pdf",
  },
  { state: "UT", url: "https://www.utah.gov/pmn/files/1278910.pdf" },
  { state: "TN", url: "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/THDA-Audited-Financial-Statement-6-30-2024-FINAL.pdf" },
  { state: "SC", url: "https://osa.sc.gov/wp-content/uploads/2024/10/Updated-SC-Housing-Financial-Statements-FY24.pdf" },
  // PA Commonwealth ACFR is NOT the PHFA report — omit until a PHFA entity PDF is available.
  { state: "ND", url: "https://www.ndhousing.nd.gov/sites/www/files/documents/Investors/AuditedFinancialStatements2024and2023.pdf" },
  { state: "MT", url: "https://archive.legmt.gov/content/Committees/Administration/audit/2024-25/Meetings/April-2025/24-07.pdf" },
  { state: "MN", url: "https://www.lrl.mn.gov/docs/2024/other/241924.pdf" },
  { state: "ME", url: "https://www.mainehousing.org/docs/default-source/financial-statements/12-31-2024-audited-financials.pdf" },
  { state: "MD", url: "https://dhcd.maryland.gov/Investors/CDABondDocs/hrb2024_06_30fs.pdf" },
  { state: "MA", url: "https://www.masshousing.com/-/media/Files/Financials/FY24_AnnualReport.pdf" },
  { state: "LA", url: "https://webapps3.lhc.la.gov/documents/BoardCommitteeMaterials/2025/January/ACM/LHC%20Financial%20Statement%20Audit%20Report%20for%20the%20FYE%20June%202024.pdf" },
  { state: "KY", url: "https://www.kyhousing.org/sites/default/files/2025-05/KHC%202024%20FS%20Report%20-%20Short-Form%20-%20FINAL.pdf" },
  { state: "KS", url: "https://admin.ks.gov/browse/files/8c8b8a0deef8464faaba21b8f4e69a24/download" },
  { state: "IN", url: "https://www.in.gov/ihcda/files/IHCDA-2024-FY-Audited-FS.pdf" },
  { state: "ID", url: "https://www.idahohousing.com/documents/2024-ihfa-financial-report.pdf" },
  { state: "HI", url: "https://files.hawaii.gov/auditor/Reports/2024_Audit/HHFDC2024.pdf" },
  { state: "GA", url: "https://open.ga.gov/openga/report/downloadFile?rid=31838" },
  { state: "DC", url: "https://dchfa.org/wp-content/uploads/2025/02/final_District-of-Columbia-HFA_FS_20242025020207.pdf" },
  { state: "AR", url: "https://adfa.arkansas.gov/wp-content/uploads/2024/12/ADFA-FS-Final-2.pdf" },
  { state: "AK", url: "https://www.ahfc.us/download_file/view/9549/583" },
  { state: "CA", url: "https://www.calhfa.ca.gov/homeownership/documents/2024-ACFR.pdf" },
  { state: "SD", url: "https://legislativeaudit.sd.gov/reports/State/Housing%20Development%20Authority%202024.pdf" },
  { state: "NM", url: "https://housingnm.org/uploads/documents/1a_FY_2024_New_Mexico_Mortgage_Finance_Authority_Audited_Finacial_Statements.pdf" },
  { state: "OK", url: "https://www.ohfa.org/wp-content/uploads/2025/01/2024-OHFA-Single-Audit-Report-FINAL.pdf" },
];

/** Corrected agency financials landing pages (not PDFs). */
const PAGE_FIXES = {
  AL: "https://www.ahfa.com/resources/investors",
  AR: "https://adfa.arkansas.gov/",
  AZ: "https://housing.az.gov/",
  CA: "https://www.calhfa.ca.gov/about/financials/reports/index.htm",
  CO: "https://www.chfainfo.com/investors/audited-financial-statements",
  CT: "https://www.chfa.org/",
  DC: "https://www.dchfa.org/",
  DE: "https://www.destatehousing.com/",
  FL: "https://www.floridahousing.org/about-florida-housing/data-docs-reports",
  GA: "https://www.dca.ga.gov/",
  HI: "https://dbedt.hawaii.gov/hhfdc/",
  IA: "https://opportunityiowa.gov/about/iowa-finance-authority/financial-reports",
  ID: "https://www.idahohousing.com/",
  IL: "https://www.ihda.org/",
  IN: "https://www.in.gov/ihcda/",
  KS: "https://kshousingcorp.org/",
  KY: "https://www.kyhousing.org/",
  LA: "https://www.lhc.la.gov/",
  MA: "https://www.masshousing.com/about/investors",
  MD: "https://dhcd.maryland.gov/Investors/Pages/default.aspx",
  ME: "https://www.mainehousing.org/about/financial-reports",
  MI: "https://www.michigan.gov/mshda",
  MN: "https://www.mnhousing.gov/",
  MO: "https://www.mhdc.com/",
  MS: "https://www.mshomecorp.com/",
  MT: "https://housing.mt.gov/",
  NC: "https://www.nchfa.com/",
  ND: "https://www.ndhfa.org/",
  NE: "https://www.nifa.org/",
  NH: "https://www.nhhousing.org/resources/publications-reports/",
  NJ: "https://nj.gov/dca/hmfa/",
  NM: "https://housingnm.org/",
  NY: "https://hcr.ny.gov/",
  OH: "https://ohiohome.org/financials/default.aspx",
  OK: "https://www.ohfa.org/",
  OR: "https://www.oregon.gov/ohcs/Pages/index.aspx",
  PA: "https://www.phfa.org/about/reports/",
  RI: "https://www.rihousing.com/",
  SC: "https://www.schousing.com/",
  SD: "https://www.sdhda.org/",
  TN: "https://thda.org/",
  TX: "https://www.tdhca.texas.gov/programs/financial-administration-division",
  UT: "https://utahhousingcorp.org/",
  VA: "https://www.virginiahousing.com/partners/investors/financial-statements",
  VT: "https://vhfa.org/partners/investors/annual-financial-statements",
  WA: "https://www.wshfc.org/finance/investor/",
  WI: "https://www.wheda.com/about-wheda/annual-report--financials",
  WV: "https://www.wvhdf.com/",
  WY: "https://www.wyomingcda.com/",
  AK: "https://www.ahfc.us/investors/financials-histori",
};

/** Corrected / replacement PDF URLs. Set null to force-clear a wrong link. */
const PDF_FIXES = {
  MA: {
    fy2024_pdf: "https://www.masshousing.com/-/media/Files/Financials/FY24_AnnualReport.pdf",
    fy2025_pdf: "https://www.masshousing.com/-/media/Files/Financials/FY25_AnnualReport.pdf",
  },
  VA: {
    fy2024_pdf:
      "https://mc-7eaf08cc-3802-4bab-9abf-a732-cdn-endpoint.azureedge.net/-/media/docs/partners/investors/financial-statements/annual-statements/2024vhdafinancialstatements_final.pdf",
    fy2025_pdf:
      "https://mc-7eaf08cc-3802-4bab-9abf-a732-cdn-endpoint.azureedge.net/-/media/docs/partners/investors/financial-statements/annual-statements/2025vhdafinancialstatements_final_public.pdf",
  },
  WI: {
    fy2025_pdf:
      "https://www.wheda.com/globalassets/documents/annual-reports-and-financials/2025/wheda-audit-fy-2025.pdf",
  },
  CO: {
    fy2024_pdf:
      "https://www.chfainfo.com/getattachment/73478f64-62be-4dbc-a9c7-137f09539fd2/chfa-2024-financials.pdf",
    fy2025_pdf:
      "https://www.chfainfo.com/getattachment/7d8e4899-6f00-428a-80e4-f45e3ea826bd/chfa-2025-financials.pdf",
  },
  CT: {
    fy2024_pdf: "https://www.chfa.org/assets/1/6/2024_Annual_Audited_Financial_Statement.pdf",
    fy2025_pdf: "https://www.chfa.org/assets/1/6/2025_Audited_Financial_Statement.pdf",
  },
  VT: {
    fy2024_pdf: "https://vhfa.org/finance/statements/fy2024-audited-financial-statements-final-w-opinionpdf",
    fy2025_pdf: "https://vhfa.org/finance/statements/fy2025-vhfa-audited-financial-packagepdf",
  },
  AL: {
    fy2024_pdf: "https://ahfa.atl1.cdn.digitaloceanspaces.com/investors/2024-ahfa-financial-statements.pdf",
    fy2025_pdf: "https://ahfa.atl1.cdn.digitaloceanspaces.com/investors/2025-ahfa-financial-statements.pdf",
  },
  ID: {
    fy2024_pdf: "https://www.idahohousing.com/documents/2024-ihfa-financial-report.pdf",
    fy2025_pdf: "https://www.idahohousing.com/documents/2025-ihfa-financial-report.pdf",
  },
  IL: {
    fy2024_pdf: "https://www.ihda.org/wp-content/uploads/2024/12/IHDA-June-30-2024-ACFR-1.pdf",
  },
  IA: {
    fy2024_pdf: "https://opportunityiowa.gov/media/6076/download?inline=",
  },
  // Commonwealth of PA ACFR is not PHFA; clear until a PHFA entity PDF is known.
  PA: { fy2024_pdf: null, fy2025_pdf: null },
  // Old nhhfa.org domain / path is dead; keep publications page only.
  NH: { fy2024_pdf: null, fy2025_pdf: null },
  // AHFC download_file/view links return HTML login/landing pages, not PDFs.
  AK: { fy2024_pdf: null, fy2025_pdf: null },
};

function checkUrl(url, redirects = 0) {
  return new Promise((resolve) => {
    if (!url) return resolve({ ok: false, status: "null" });
    let parsed;
    try {
      parsed = new URL(url);
    } catch {
      return resolve({ ok: false, status: "badurl" });
    }
    const lib = parsed.protocol === "https:" ? https : http;
    const req = lib.request(
      url,
      {
        method: "GET",
        timeout: 20000,
        headers: {
          "User-Agent": "Mozilla/5.0 (compatible; HFALinkChecker/1.0)",
          Range: "bytes=0-15",
          Accept: "*/*",
        },
      },
      (res) => {
        const status = res.statusCode;
        const loc = res.headers.location || null;
        if (status >= 300 && status < 400 && loc && redirects < 5) {
          res.resume();
          return resolve(checkUrl(new URL(loc, url).href, redirects + 1));
        }
        const chunks = [];
        res.on("data", (c) => chunks.push(c));
        res.on("end", () => {
          const buf = Buffer.concat(chunks);
          const isPdf = buf.slice(0, 5).toString() === "%PDF-";
          const type = res.headers["content-type"] || "";
          let ok = status === 200 || status === 206;
          if ([404, 410, 403].includes(status)) ok = false;
          if (/text\/html/i.test(type) || /<!doctype html|<html/i.test(buf.toString("utf8"))) ok = false;
          if (isPdf) ok = true;
          resolve({ ok, status, loc, type, isPdf, final: url });
        });
      }
    );
    req.on("error", (e) => resolve({ ok: false, status: "err", err: e.message }));
    req.on("timeout", () => {
      req.destroy();
      resolve({ ok: false, status: "timeout" });
    });
    req.end();
  });
}

function pickPage(st, cat) {
  if (PAGE_FIXES[st]) return PAGE_FIXES[st];
  if (cat?.urls?.length) {
    // Prefer non-PDF catalog URLs
    const html = cat.urls.find((u) => !/\.pdf($|\?)/i.test(u));
    if (html) return html;
  }
  if (cat?.direct_pdfs?.length) return null; // don't use PDF as "page"
  return cat?.urls?.[0] || null;
}

async function main() {
  const byDirect = Object.fromEntries(direct.map((r) => [r.state, r.url]));
  const byManual24 = Object.fromEntries(MANUAL_FY2024.map((r) => [r.state, r.url]));
  const out = {};

  for (const cat of catalog) {
    const st = cat.state;
    const l24 = log24[st];
    const l25 = log25[st];

    let page_url = pickPage(st, cat);

    const fix = PDF_FIXES[st] || {};
    let fy2025_pdf =
      Object.prototype.hasOwnProperty.call(fix, "fy2025_pdf")
        ? fix.fy2025_pdf
        : byDirect[st] || (l25?.candidates?.[0] ?? null);
    let fy2024_pdf = Object.prototype.hasOwnProperty.call(fix, "fy2024_pdf")
      ? fix.fy2024_pdf
      : (l24?.downloaded && l24.url ? l24.url : null) || byManual24[st] || null;

    // CO previously duplicated the same attachment for 2024/2025.
    if (fy2024_pdf && fy2025_pdf && fy2024_pdf === fy2025_pdf) {
      // Prefer distinct archive GUID for FY2024 when collision remains.
      fy2024_pdf =
        "https://www.chfainfo.com/getattachment/73478f64-62be-4dbc-a9c7-137f09539fd2/chfa-2024-financials.pdf";
    }

    out[st] = {
      state: st,
      hfa_name: cat.name,
      hfa_abbr: cat.abbr,
      page_url,
      fy2024_pdf,
      fy2025_pdf,
    };
  }

  // Validate and clear broken PDF links
  const cleared = [];
  for (const [st, row] of Object.entries(out)) {
    for (const key of ["fy2024_pdf", "fy2025_pdf"]) {
      const url = row[key];
      if (!url) continue;
      const res = await checkUrl(url);
      if (!res.ok) {
        cleared.push({ st, key, url, status: res.status, loc: res.loc, err: res.err });
        row[key] = null;
      }
    }
    // Soft-check pages; if broken keep PAGE_FIXES already applied, else try leave as-is
    if (row.page_url) {
      const res = await checkUrl(row.page_url);
      // Many agency sites block bots with 403/404; keep PAGE_FIXES / curated pages anyway.
      // Only clear if DNS failure.
      if (res.status === "err" && /ENOTFOUND/i.test(res.err || "")) {
        cleared.push({ st, key: "page_url", url: row.page_url, status: res.status, err: res.err });
        // fallback to root-like PAGE_FIXES already preferred; if still bad, null
        if (!PAGE_FIXES[st]) row.page_url = null;
      }
    }
  }

  // Sort keys
  const sorted = Object.keys(out)
    .sort()
    .reduce((a, k) => {
      a[k] = out[k];
      return a;
    }, {});

  fs.writeFileSync("docs/hfa_report_links.json", JSON.stringify(sorted, null, 2));
  fs.writeFileSync("docs/_link_fix_cleared.json", JSON.stringify(cleared, null, 2));

  const counts = {
    states: Object.keys(sorted).length,
    page: Object.values(sorted).filter((x) => x.page_url).length,
    fy24: Object.values(sorted).filter((x) => x.fy2024_pdf).length,
    fy25: Object.values(sorted).filter((x) => x.fy2025_pdf).length,
    cleared: cleared.length,
  };
  console.log(JSON.stringify(counts, null, 2));
  console.log("Cleared broken PDFs:", cleared.length);
  for (const c of cleared.slice(0, 40)) {
    console.log(c.st, c.key, c.status, (c.url || "").slice(0, 90));
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
