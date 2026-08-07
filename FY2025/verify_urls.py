import re, requests

pages = {
    'WCDA': 'https://www.wyomingcda.com/investors/',
    'VHFA': 'https://vhfa.org/partners/investors/annual-financial-statements',
    'KY': 'https://www.kyhousing.org/page/financial-information',
    'OHFA': 'https://www.ohfa.org/financials/',
    'NM': 'https://housingnm.org/about-us/financials',
    'AK': 'https://www.ahfc.us/investors/financials-histori',
    'DCHFA': 'https://dchfa.org/investors/audited-financial-statements/',
    'RI': 'https://www.rihousingbonds.com/housing-investor-relations/documents/downloads/i938',
    'NIFA': 'https://www.nifabonds.bondlink.com/nebraska-investment-finance-authority-ne/documents/downloads/i6610?docTypeId=41597',
}
for name, url in pages.items():
    print('===', name, '===')
    try:
        r = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
        html = r.text
        found = set()
        for pat in [
            r'https?://[^"\']+\.pdf[^"\']*',
            r'href="([^"]+\.pdf[^"]*)"',
            r'href="(/documents/download/\d+)"',
            r'href="([^"]*uploads[^"]+\.pdf[^"]*)"',
            r'href="([^"]*wp-content[^"]+\.pdf[^"]*)"',
            r'href="([^"]*sites/default/files[^"]+\.pdf[^"]*)"',
            r'href="([^"]*getattachment[^"]+\.pdf[^"]*)"',
            r'href="([^"]*download_file/view/[^"]+)"',
        ]:
            for m in re.findall(pat, html, re.I):
                val = m if isinstance(m, str) else m
                if val.startswith('/'):
                    val = requests.compat.urljoin(url, val)
                found.add(val)
        for x in sorted(found):
            print(x)
    except Exception as e:
        print('ERR', e)

tests = [
    'https://www.idahohousing.com/documents/2025-ihfa-financial-report.pdf',
    'https://sos.oregon.gov/audits/Documents/2025-26.pdf',
    'https://archive.legmt.gov/content/Committees/Administration/audit/2025-26/Meetings/April-2026/25-07.pdf',
    'https://www.ohfa.org/wp-content/uploads/2026/01/2025-OHFA-Single-Audit-Report-FINAL.pdf',
    'https://legislativeaudit.sd.gov/reports/State/Housing%20Development%20Authority%202025.pdf',
    'https://legislativeaudit.sd.gov/reports/State/Housing%20Development%20Authority%20Single%20Audit%202025.pdf',
    'https://www.kyhousing.org/sites/default/files/2026-03/KHC%202025%20FS%20Report.pdf',
    'https://www.kyhousing.org/sites/default/files/2026-03/KHC%202025%20FS.pdf',
    'https://www.wyomingcda.com/wp-content/uploads/2025/12/2025-Audited-Financial-Statements-WCDA.pdf',
    'https://www.wyomingcda.com/wp-content/uploads/2025/12/WCDA-2025-AFS.pdf',
    'https://vhfa.org/sites/default/files/uploads/2025/09/VHFA-Financial-Statements-and-Required-Supplementary-Information-June-30-2025.pdf',
    'https://vhfa.org/sites/default/files/uploads/2025/09/2025-VHFA-Financial-Statements.pdf',
    'https://www.rihousingbonds.com/housing-investor-relations/documents/download/13342',
    'https://www.rihousingbonds.com/housing-investor-relations/documents/download/13341',
    'https://www.nifabonds.bondlink.com/nebraska-investment-finance-authority-ne/documents/download/12345',
    'https://housingnm.org/uploads/documents/NMMFA_Financial_Statement_Audit_2025.pdf',
    'https://www.ahfc.us/application/files/9718/5891/1872/2025-06-30-fin-stmts-ahfc-audited.pdf',
    'https://www.ahfc.us/application/files/8918/5891/1872/2025-06-30-financial-statements-ahfc-audited.pdf',
    'https://www.ahfc.us/application/files/8918/9696/1107/2025-06-30-fin-stmts-ahfc-audited.pdf',
    'https://www.ahfc.us/application/files/9718/9696/1107/2025-06-30-fin-stmts-ahfc-audited.pdf',
    'https://www.ahfc.us/application/files/9918/5891/1872/2025-06-30-financial-statements-ahfc-audited.pdf',
    'https://www.ahfc.us/application/files/9917/5891/1872/2025-06-30-financial-statements-ahfc-audited.pdf',
    'https://www.ahfc.us/application/files/9916/9696/1107/2025-06-30-fin-stmts-ahfc-audited.pdf',
    'https://www.ahfc.us/application/files/9917/9696/1107/2025-06-30-fin-stmts-ahfc-audited.pdf',
    'https://www.ahfc.us/application/files/9918/9696/1107/2025-06-30-fin-stmts-ahfc-audited.pdf',
    'https://www.ahfc.us/application/files/9919/5891/1872/2025-06-30-financial-statements-ahfc-audited.pdf',
    'https://www.ahfc.us/application/files/9919/9696/1107/2025-06-30-fin-stmts-ahfc-audited.pdf',
    'https://www.ahfc.us/application/files/9916/5891/1872/2025-06-30-financial-statements-ahfc-audited.pdf',
    'https://www.ahfc.us/application/files/9916/5891/1872/2025-06-30-fin-stmts-ahfc-audited.pdf',
    'https://www.ahfc.us/application/files/9917/5891/1872/2025-06-30-fin-stmts-ahfc-audited.pdf',
    'https://www.ahfc.us/application/files/9918/5891/1872/2025-06-30-fin-stmts-ahfc-audited.pdf',
]
print('\n=== VERIFY ===')
for u in tests:
    try:
        r = requests.get(u, timeout=30, stream=True, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=True)
        ct = r.headers.get('content-type', '')
        chunk = r.raw.read(8)
        sig = chunk.decode('latin1', 'replace')
        final = r.url
        print(r.status_code, ct[:40], sig, final)
    except Exception as e:
        print('ERR', u, e)
