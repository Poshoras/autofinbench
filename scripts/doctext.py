"""Fetch a filing's primary document and return plain text (for independent text verification)."""
import sys, os, re, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edgar

def text(cik, accn):
    doc = next(f['doc'] for f in edgar.filings(cik) if f['accn'] == accn)
    raw = edgar.primary_doc(cik, accn, doc)
    raw = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', raw)
    raw = re.sub(r'(?is)<ix:header>.*?</ix:header>', ' ', raw)   # hidden iXBRL header
    t = re.sub(r'<[^>]+>', ' ', raw)
    t = html.unescape(t).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', t)

def find(t, pattern, width=110, limit=5):
    return [t[max(0, m.start()-width): m.end()+width] for m in list(re.finditer(pattern, t, re.I))[:limit]]

if __name__ == '__main__':
    t = text(int(sys.argv[1]), sys.argv[2])
    for s in find(t, sys.argv[3], limit=int(sys.argv[4]) if len(sys.argv) > 4 else 5): print('…', s, '…\n')
