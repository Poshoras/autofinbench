"""Stronger derivability check for missing-premise items (v2).

v1 (make_ops.py) only looked for a +/- b (+/- c) over all numbers in the excerpt, which misses
longer identities such as Net sales - SG&A - impairment - operating income = COGS.
v2 works table by table on the ORIGINAL seed excerpt:
  * a row is a list of period values (k-th number in the row = k-th period column);
  * a candidate identity is a signed combination of other rows (up to 4 rows, or any contiguous block)
    or a 2-row product/ratio (with x1, x1000, /1000 scaling);
  * it counts only if it reproduces the removed row in EVERY period column (an accounting identity holds
    for all periods; a coincidence almost never does).
Writes step1/derivability_v2.json. Usage: python3 -I scripts/derivability_v2.py"""
import json, os, re, itertools, glob
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
S1 = os.path.join(ROOT, 'step1')
SECQUE = os.path.join(ROOT, '..', 'data', 'secque_full')

TOK = re.compile(r'^\(?-?\$?\s*\(?(\d[\d,]*\.?\d*)\)?%?$')

def cell_value(c):
    c = c.strip().replace('$', '').strip()
    if c in ('—', '–', '-', '—%'): return 0.0
    m = TOK.match(c)
    if not m: return None
    v = float(m.group(1).replace(',', ''))
    return -v if c.startswith('(') or c.endswith(')') or c.startswith('-') else v

def tables(ctx):
    out, cur = [], []
    for line in ctx.split('\n'):
        if line.startswith('|'): cur.append(line)
        elif cur: out.append(cur); cur = []
    if cur: out.append(cur)
    return out

def parse(tbl):
    rows = []
    for line in tbl:
        cells = line.strip().strip('|').split('|')
        if len(cells) < 3 or set(cells[1].strip()) <= set('-:'): continue
        label = cells[1].strip()
        vals = [v for v in (cell_value(c) for c in cells[2:]) if v is not None]
        if not label or not vals: continue
        if all(1990 <= abs(v) <= 2035 and float(v).is_integer() for v in vals): continue  # header row of years
        rows.append((label, vals))
    if not rows: return [], 0
    counts = {}
    for _, v in rows: counts[len(v)] = counts.get(len(v), 0) + 1
    P = max(counts, key=lambda k: (counts[k], k))
    return [(l, v) for l, v in rows if len(v) == P], P

def close(a, b, tol): return all(abs(x - y) <= tol for x, y in zip(a, b))

def search(rows, t_idx, tol):
    target = rows[t_idx][1]
    others = [(i, r) for i, r in enumerate(rows) if i != t_idx and not close(r[1], target, tol) and any(r[1])]
    hits = []
    # signed combinations of up to 4 rows
    for k in range(1, 5):
        for combo in itertools.combinations(others, k):
            for signs in itertools.product((1, -1), repeat=k):
                s = [sum(sg * r[1][p] for sg, (_, r) in zip(signs, combo)) for p in range(len(target))]
                if close(s, target, tol * k) or close([-x for x in s], target, tol * k):
                    hits.append(' '.join(f"{'+' if sg > 0 else '-'} [{r[0][:45]}]" for sg, (_, r) in zip(signs, combo)))
                    if len(hits) > 20: return hits
    # contiguous blocks (subtotals), any length
    for a in range(len(rows)):
        for b in range(a + 5, len(rows) + 1):
            if a <= t_idx < b: continue
            s = [sum(rows[i][1][p] for i in range(a, b)) for p in range(len(target))]
            if close(s, target, tol * 3) or close([-x for x in s], target, tol * 3):
                hits.append(f'sum of rows [{rows[a][0][:30]}] .. [{rows[b-1][0][:30]}]')
    # 2-row products / ratios with unit scaling
    for (i, r1), (j, r2) in itertools.permutations(others, 2):
        for sc in (1, 1000, 1 / 1000):
            for name, f in (('/', lambda x, y: x / y * sc if y else None), ('*', lambda x, y: x * y * sc)):
                vals = [f(x, y) for x, y in zip(r1[1], r2[1])]
                if None in vals: continue
                if all(t and abs(v - t) <= max(abs(t) * 0.005, tol) for v, t in zip(vals, target)):
                    hits.append(f'[{r1[0][:40]}] {name} [{r2[0][:40]}] (x{sc:g})')
    return hits

def main():
    seeds = {}
    for f in glob.glob(os.path.join(SECQUE, '*.jsonl')):
        for l in open(f):
            d = json.loads(l); seeds[d['QID']] = d
    items = [json.loads(l) for l in open(os.path.join(S1, 'items_final.jsonl'))]
    out = {}
    for it in items:
        if it['op'] not in ('missing', 'reconstruct') or 'removed_renderings' not in it: continue
        ctx = seeds[it['seed_qid']]['context_markdown_with_headers']
        forms = it['removed_renderings']
        res = []
        for tbl in tables(ctx):
            rows, P = parse(tbl)
            for ti, (label, vals) in enumerate(rows):
                hit_pos = [p for p, v in enumerate(vals) if any(abs(abs(v) - float(f.replace(',', ''))) < 1e-6 for f in forms)]
                if not hit_pos: continue
                tol = 0.015 if any(not float(x).is_integer() for x in vals) else 1.5
                h = search(rows, ti, tol) if P >= 2 else []
                res.append(dict(table_row=label, n_period_columns=P, identities_all_columns=h[:8],
                                note='single period column: identity cannot be cross-checked' if P < 2 else ''))
        out[it['item_id']] = dict(op=it['op'], seed_qid=it['seed_qid'], company=it['company'], removed=forms[0], tables=res)
        n = sum(len(r['identities_all_columns']) for r in res)
        print(f"{it['seed_qid']:9} {it['op']:11} rows={len(res)} identities={n}")
        for r in res:
            for h in r['identities_all_columns'][:3]: print('      ', r['table_row'][:40], '=', h)
    json.dump(out, open(os.path.join(S1, 'derivability_v2.json'), 'w'), indent=1, ensure_ascii=False)

if __name__ == '__main__':
    main()
