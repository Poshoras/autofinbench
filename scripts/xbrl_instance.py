"""Parse a filing's full XBRL instance (incl. dimensional/segment facts).
Usage as module: facts = load(cik, accn); query(facts, concept, end=..., start=..., dims={...})"""
import sys, os, json, re
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edgar

PARSED = os.path.join(edgar.CACHE, 'parsed'); os.makedirs(PARSED, exist_ok=True)

def _index(cik, accn):
    base = f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace("-", "")}'
    data = edgar._get(base + '/index.json', os.path.join(edgar.CACHE, f'idx_{accn}.json'))
    return base, [i['name'] for i in json.loads(data)['directory']['item']]

def instance_name(names):
    for n in names:
        if n.endswith('_htm.xml'): return n
    for n in names:
        if n.endswith('.xml') and not re.search(r'(_cal|_def|_lab|_pre|FilingSummary)', n) and not n.startswith('Financial_Report'):
            return n
    raise RuntimeError('no XBRL instance found')

def load(cik, accn):
    out = os.path.join(PARSED, f'{accn}.json')
    if os.path.exists(out): return json.load(open(out))
    base, names = _index(cik, accn)
    inst = instance_name(names)
    raw = edgar._get(f'{base}/{inst}', os.path.join(edgar.CACHE, f'inst_{accn}.xml'))
    root = ET.fromstring(raw)
    X = '{http://www.xbrl.org/2003/instance}'
    ctx = {}
    for c in root.iter(X + 'context'):
        p = c.find(X + 'period')
        inst_ = p.find(X + 'instant')
        per = {'instant': inst_.text.strip()} if inst_ is not None else \
              {'start': p.find(X + 'startDate').text.strip(), 'end': p.find(X + 'endDate').text.strip()}
        dims = {}
        for m in c.iter('{http://xbrl.org/2006/xbrldi}explicitMember'):
            dims[m.get('dimension').split(':')[-1]] = m.text.strip().split(':')[-1]
        ctx[c.get('id')] = dict(per, dims=dims)
    facts = []
    for el in root:
        cref = el.get('contextRef')
        if not cref or el.text is None: continue
        tag = el.tag.split('}')[-1]
        ns = el.tag.split('}')[0].strip('{')
        prefix = 'us-gaap' if 'fasb.org/us-gaap' in ns else ('dei' if '/dei/' in ns else ns.rsplit('/', 2)[-2] if ns.count('/') > 2 else ns)
        try: val = float(el.text.strip())
        except ValueError: continue
        c = ctx[cref]
        facts.append(dict(concept=tag, prefix=prefix, val=val, unit=el.get('unitRef'),
                          decimals=el.get('decimals'), **{k: v for k, v in c.items()}))
    json.dump(dict(instance=f'{base}/{inst}', facts=facts), open(out, 'w'))
    return dict(instance=f'{base}/{inst}', facts=facts)

def query(doc, concept, end, start=None, dims=None):
    """Exact-period lookup. end = instant date (if start None) or duration end. dims={} means no dimensions."""
    dims = dims or {}
    hits = []
    for f in doc['facts']:
        if f['concept'] != concept or f['dims'] != dims: continue
        if start is None and f.get('instant') == end: hits.append(f)
        elif start is not None and f.get('start') == start and f.get('end') == end: hits.append(f)
    vals = {h['val'] for h in hits}
    if len(vals) > 1: raise RuntimeError(f'conflicting values for {concept} {start}->{end} {dims}: {vals}')
    return hits[0] if hits else None

if __name__ == '__main__':
    cik, accn = sys.argv[1], sys.argv[2]
    d = load(cik, accn)
    pat = re.compile(sys.argv[3]) if len(sys.argv) > 3 else None
    print(d['instance'], len(d['facts']), 'facts')
    for f in d['facts']:
        if pat and not pat.search(f['concept'] + ' ' + json.dumps(f['dims'])): continue
        per = f.get('instant') or f"{f.get('start')}->{f.get('end')}"
        print(f"  {f['concept']:<60} {per:<24} {f['val']:>20,.2f} {json.dumps(f['dims']) if f['dims'] else ''}")
