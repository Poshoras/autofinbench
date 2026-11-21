"""Filing excerpts for items that have no SecQue context (trend, cross).
For every filing an item relies on, take the HTML tables of that filing that contain the item's input
values (greedy cover, financial statements preferred), with the text just before each table as caption.
Writes step1/eval/contexts.json. Usage: python3 -I scripts/build_contexts.py"""
import json, os, re, sys, html
from html.parser import HTMLParser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edgar
import make_ops as M
from xbrl_series import anniversaries

ROOT = M.ROOT
OUT = os.path.join(ROOT, 'step1', 'eval'); os.makedirs(OUT, exist_ok=True)

class Tables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.depth, self.text = [], 0, []
        self.row = self.cell = None
    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.depth += 1
            if self.depth == 1:
                cap = re.sub(r'\s+', ' ', ''.join(self.text[-400:])).strip()[-220:]
                self.tables.append(dict(caption=cap, rows=[])); self.text = []
        elif self.depth and tag == 'tr': self.row = []
        elif self.depth and tag in ('td', 'th'): self.cell = []
        elif tag in ('br', 'p', 'div') and not self.depth: self.text.append(' ')
    def handle_endtag(self, tag):
        if tag == 'table' and self.depth: self.depth -= 1
        elif self.depth and tag in ('td', 'th') and self.cell is not None and self.row is not None:
            self.row.append(re.sub(r'\s+', ' ', ''.join(self.cell)).strip()); self.cell = None
        elif self.depth and tag == 'tr' and self.row is not None:
            if any(self.row): self.tables[-1]['rows'].append(self.row)
            self.row = None
    def handle_data(self, d):
        if self.depth and self.cell is not None: self.cell.append(d)
        elif not self.depth: self.text.append(d)

def tidy_row(cells):
    out = []
    for c in cells:
        c = c.replace('\xa0', ' ').strip()
        if not c: continue
        if out and (c in (')', '%', ')%') or (out[-1] in ('$', '(', '$(') and c[0].isdigit())):
            out[-1] = (out[-1] + c).replace('$', '$ ').replace('$ (', '$(').strip(); continue
        out.append(c)
    return out

def render(t):
    rows = [tidy_row(r) for r in t['rows']]
    rows = [r for r in rows if r]
    body = '\n'.join('| ' + ' | '.join(r) + ' |' for r in rows)
    return (t['caption'] + '\n' if t['caption'] else '') + body

LEAF = re.compile(r'<div[^>]*style="([^"]*)"[^>]*>((?:(?!<div).)*?)</div>', re.S)
def positioned_pages(raw):
    """Rebuild page 'tables' from absolutely positioned text boxes: one row per y position, cells ordered by x."""
    pages, cur, last_top = [], {}, -1
    for m in LEAF.finditer(raw):
        st = m.group(1); top = re.search(r'top:(\d+)px', st); left = re.search(r'left:(\d+)px', st)
        if not top or not left: continue
        txt = html.unescape(re.sub(r'<[^>]+>', '', m.group(2))).replace('\xa0', ' ').strip()
        if not txt: continue
        y, x = int(top.group(1)), int(left.group(1))
        if y < last_top - 300 and cur: pages.append(cur); cur = {}
        last_top = y
        key = next((k for k in cur if abs(k - y) <= 3), y)
        cur.setdefault(key, []).append((x, txt))
    if cur: pages.append(cur)
    out = []
    for pg in pages:
        rows = [[t for _, t in sorted(cells)] for _, cells in sorted(pg.items())]
        out.append(dict(caption='', rows=rows))
    return out

_docs = {}
def filing_tables(cik, accn, exhibits=False):
    key = (cik, accn, exhibits)
    if key in _docs: return _docs[key]
    idx = json.loads(edgar._get(f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace("-","")}/index.json',
                                os.path.join(edgar.CACHE, f'idx_{accn}.json')))
    htm = [i for i in idx['directory']['item'] if i['name'].lower().endswith('.htm') and not re.match(r'(?i)r\d+\.htm', i['name'])]
    prim = next((f['doc'] for f in edgar.filings(cik) if f['accn'] == accn), None)
    if prim is None:
        prim = max([i for i in htm if not re.search(r'(?i)ex', i['name'])], key=lambda i: int(i.get('size') or 0))['name']
    names = [prim] if not exhibits else [i['name'] for i in htm if re.search(r'(?i)ex-?13|ex13', i['name'])]
    tabs = []
    for n in names:
        raw = edgar.primary_doc(cik, accn, n)
        p = Tables(); p.feed(raw)
        if not p.tables: p.tables = positioned_pages(raw)  # PDF-style filings: absolutely positioned <div>s, no <table>
        for t in p.tables:
            t['doc'] = n; t['flat'] = ' '.join(c for r in t['rows'] for c in r).replace('\xa0', ' ')
        tabs += [t for t in p.tables if t['rows']]
    _docs[key] = tabs
    return tabs

def patterns(val):
    """(patterns, big): big=False for figures under $100m in whole millions, whose short digits only count inside an already chosen table."""
    small = abs(val) < 1e8 and abs(val) >= 1e6 and abs(val) % 1e6 == 0
    forms = {f'{abs(val) / 1e6:,.0f}'} if small else M.renderings(val)
    return [re.compile(r'(?<![\d.,])' + re.escape(f) + r'(?![\d]|,\d|\.\d)') for f in forms], not small

def excerpt(cik, accn, needs):
    """needs: {name: value}. Returns (text, coverage)."""
    chosen, cover = [], {}
    for exhibits in (False, True):
        tabs = filing_tables(cik, accn, exhibits)
        hits = {}
        for ti, t in enumerate(tabs):
            for n, v in needs.items():
                if n in cover: continue
                pats, big = patterns(v)
                if big and any(p.search(t['flat']) for p in pats): hits.setdefault(ti, set()).add(n)
        while hits:
            score = lambda ti: (len(hits[ti]), bool(re.search(r'(?i)consolidated|statements? of', tabs[ti]['caption'])), len(tabs[ti]['rows']))
            ti = max(hits, key=score)
            chosen.append(tabs[ti])
            for n in hits[ti]: cover[n] = f"{tabs[ti]['doc']} table {ti}"
            done = hits.pop(ti)
            hits = {k: v - done for k, v in hits.items() if v - done}
        # small numbers (e.g. 2-digit $m): accept only inside a table already chosen
        for n, v in needs.items():
            if n in cover: continue
            pats, big = patterns(v)
            if not big:
                for t in chosen:
                    if any(p.search(t['flat']) for p in pats): cover[n] = f"{t['doc']} (small number, inside chosen table)"; break
        if len(cover) == len(needs): break
    return '\n\n'.join(render(t) for t in chosen), cover

def header(cik, accn, form_hint):
    f = next((f for f in edgar.filings(cik) if f['accn'] == accn), None)
    if f: return f"{f['form']} for the period ended {f['period']} (filed {f['filed']}, accession {accn})"
    return f"{form_hint} (accession {accn})"

def needs_by_filing(s, end):
    _, inp = M.compute(s, end, 'first')
    by = {}
    for n, x in inp.items():
        accn = inp[n[:-5]]['first_accn'] if n.endswith('_prev') and x.get('base_from_same_filing') is not False else x['first_accn']
        by.setdefault(accn, {})[n] = x['used']
    return by

def main():
    seeds = {s['qid']: s for s in json.load(open(os.path.join(ROOT, 'step1', 'seeds.json')))}
    items = [json.loads(l) for l in open(os.path.join(ROOT, 'step1', 'items_final.jsonl'))]
    out = {}
    for it in items:
        if it['op'] not in ('trend', 'cross') or it['status'] == 'REJECTED': continue
        s = seeds[it['seed_qid']]
        form_hint = '10-K' if s['months'] == 12 else '10-Q' if s['months'] in (3, 6, 9) else 'filing'
        parts, prov = [], []
        if it['op'] == 'trend':
            jobs = [(s, e) for e in anniversaries(s['end'], 5)]
        else:
            pr = s['peer']
            jobs = [(s, s['end']), (dict(s, company=pr['company'], cik=pr['cik'], items=pr.get('items', s['items'])), pr['end'])]
        for ss, e in jobs:
            for accn, needs in needs_by_filing(ss, e).items():
                text, cov = excerpt(ss['cik'], accn, needs)
                parts.append(f"=== {ss['company']} {header(ss['cik'], accn, form_hint)} ===\n{text}")
                prov.append(dict(company=ss['company'], period_end=e, accn=accn, needs={k: v for k, v in needs.items()},
                                 covered=cov, missing=[n for n in needs if n not in cov]))
        ctx = '\n\n'.join(parts)
        out[it['item_id']] = dict(context=ctx, n_chars=len(ctx), sources=prov)
        miss = [(p['period_end'], p['missing']) for p in prov if p['missing']]
        print(f"{it['item_id']:24} chars={len(ctx):7} missing={miss}", flush=True)
    json.dump(out, open(os.path.join(OUT, 'contexts.json'), 'w'), indent=1, ensure_ascii=False)

if __name__ == '__main__':
    main()
