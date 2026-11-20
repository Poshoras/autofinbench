"""Thin cached client for SEC EDGAR (submissions, companyfacts, filing documents).
Raw responses are cached under data/edgar/ (treated as untrusted data)."""
import json, os, time, urllib.request, gzip, io

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CACHE = os.path.join(ROOT, 'data', 'edgar')
UA = 'AutoFinBench-research-script/0.1 (academic research)'
os.makedirs(CACHE, exist_ok=True)

def _get(url, path):
    if os.path.exists(path):
        return open(path, 'rb').read()
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'gzip'})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
        if r.headers.get('Content-Encoding') == 'gzip':
            data = gzip.decompress(data)
    with open(path, 'wb') as f:
        f.write(data)
    time.sleep(0.2)  # stay well under SEC's 10 req/s limit
    return data

def submissions(cik):
    return json.loads(_get(f'https://data.sec.gov/submissions/CIK{int(cik):010d}.json',
                           os.path.join(CACHE, f'sub_{int(cik)}.json')))

def companyfacts(cik):
    return json.loads(_get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json',
                           os.path.join(CACHE, f'facts_{int(cik)}.json')))

def filings(cik, forms=('10-K', '10-Q')):
    r = submissions(cik)['filings']['recent']
    out = []
    for i, f in enumerate(r['form']):
        if f in forms:
            out.append(dict(form=f, period=r['reportDate'][i], filed=r['filingDate'][i],
                            accn=r['accessionNumber'][i], doc=r['primaryDocument'][i]))
    return out

def primary_doc(cik, accn, doc):
    """Download the filing's primary HTML document (for independent verification)."""
    d = os.path.join(CACHE, 'docs'); os.makedirs(d, exist_ok=True)
    url = f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace("-", "")}/{doc}'
    return _get(url, os.path.join(d, f'{accn}_{doc}')).decode('utf-8', 'replace')
