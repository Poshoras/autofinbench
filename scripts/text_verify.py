"""Independent second source for trend-item inputs: is each XBRL value printed in the filing's own HTML text?
Writes step1/text_verify.json. Usage: python3 -I scripts/text_verify.py"""
import json, os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edgar
from xbrl_series import anniversaries
import make_ops as M

ROOT = M.ROOT
_cache = {}
def doc_text(cik, accn):
    if (cik, accn) in _cache: return _cache[(cik, accn)]
    doc = next((f['doc'] for f in edgar.filings(cik) if f['accn'] == accn), None)
    if doc is None:  # older filing not in 'recent': pick the largest non-exhibit .htm in the filing index
        idx = json.loads(edgar._get(f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace("-","")}/index.json',
                                    os.path.join(edgar.CACHE, f'idx_{accn}.json')))
        htm = [i for i in idx['directory']['item'] if i['name'].lower().endswith('.htm') and not re.search(r'(?i)ex|^r\d', i['name'])]
        doc = max(htm, key=lambda i: int(i.get('size') or 0))['name']
    raw = edgar.primary_doc(cik, accn, doc)
    raw = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', raw)
    raw = re.sub(r'(?is)<ix:header>.*?</ix:header>', ' ', raw)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', raw)).replace('\xa0', ' ')
    _cache[(cik, accn)] = re.sub(r'\s+', ' ', t)
    return _cache[(cik, accn)]

def main():
    S = json.load(open(os.path.join(ROOT, 'step1', 'seeds.json')))
    out = []
    for s in S:
        for e in anniversaries(s['end'], 5):
            v, inp = M.compute(s, e, 'first')
            for n, x in inp.items():
                accn = x['first_accn'] if not n.endswith('_prev') or x.get('base_from_same_filing') is False else inp[n[:-5]]['first_accn']
                try:
                    t = doc_text(s['cik'], accn)
                    found = any(re.search(r'(?<![\d.,])' + re.escape(r) + r'(?![\d]|,\d|\.\d)', t) for r in M.renderings(x['used']))
                except Exception as ex:
                    found = None; print('ERR', s['qid'], accn, ex)
                out.append(dict(qid=s['qid'], period=e, item=n, concept=x['concept'], value=x['used'], accn=accn, found_in_text=found))
        f = [o for o in out if o['qid'] == s['qid']]
        print(s['qid'], sum(1 for o in f if o['found_in_text']), '/', len(f), flush=True)
    json.dump(out, open(os.path.join(ROOT, 'step1', 'text_verify.json'), 'w'), indent=1)
    print('total', sum(1 for o in out if o['found_in_text']), '/', len(out))

if __name__ == '__main__':
    main()
