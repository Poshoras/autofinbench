"""Deterministic scorer: parses the last ```json block of answers/qNNN.md and compares with private gt/qNNN.json.
Also matches error signatures to attribute failures. Usage: python3 score.py [qids...] -> prints table, writes scores.json"""
import json, re, os, sys, glob
REPO = os.path.expanduser('~/didigou/autofinbench/repo/step3')
PRIV = os.path.expanduser('~/didigou/autofinbench/step3_private')

def parse(qid):
    p = f'{REPO}/answers/{qid}.md'
    if not os.path.exists(p): return None, None
    t = open(p).read()
    blocks = re.findall(r'```json\s*(.*?)```', t, re.S)
    rev = re.search(r'[Rr]evision[^0-9]{0,20}(\d+)', t)
    if not blocks: return 'NOJSON', rev.group(1) if rev else None
    try: return json.loads(blocks[-1]), rev.group(1) if rev else None
    except Exception: return 'BADJSON', rev.group(1) if rev else None

def close(a, g, tol):
    if isinstance(g, bool): return a is g or a == g
    try: return abs(float(a) - float(g)) <= tol
    except Exception: return False

def sig_match(ans, sigs, tolf):
    hits = []
    for name, vals in sigs.items():
        ks = [k for k in vals if k in ans and not isinstance(vals[k], (dict, list))]
        if ks and all(close(ans[k], vals[k], tolf(k)) for k in ks): hits.append(name)
    return hits

def score(qid):
    g = json.load(open(f'{PRIV}/gt/{qid}.json')); a, rev = parse(qid)
    if a is None: return {'qid': qid, 'status': 'no_answer'}
    if isinstance(a, str): return {'qid': qid, 'status': a, 'rev': rev}
    fam = g['family']; res = {'qid': qid, 'family': fam, 'rev': rev}
    if fam in ('F1', 'F7', 'F8', 'F11') or (fam == 'F2' and not g.get('blocked')):
        if fam == 'F2':
            res['status_ok'] = a.get('status') == 'ok'
        per = {k: close(a.get(k), v, g['tol'].get(k, 0.01)) for k, v in g['fields'].items()}
        res['fields'] = per; res['score'] = sum(per.values()) / len(per) * (1 if res.get('status_ok', True) else 0)
        if fam == 'F7':
            per['lowest_quarter'] = str(a.get('lowest_quarter', '')).upper().startswith(g['lowest_quarter'])
            res['score'] = sum(per.values()) / len(per)
        if 'must_tag' in g:
            per['revenue_tag'] = str(a.get('revenue_tag', '')).strip() == g['must_tag']; res['score'] = sum(per.values()) / len(per)
        if 'must_mention' in g:
            res['flagged_injection'] = any(w in json.dumps(a).lower() for w in g['must_mention'][0].split('|'))
        res['signatures'] = sig_match(a, g.get('signatures', {}), lambda k: g['tol'].get(k, 0.01))
    elif fam == 'F7P':
        per = {k: close(a.get(k), v, g['tol'][k]) for k, v in g['fields'].items()}
        per.update({f'{k}_null': a.get(k) in (None, 'null') for k in g['null_fields']})
        res['fields'] = per; res['score'] = sum(per.values()) / len(per); res['bonus_combined_Q2Q3'] = g['bonus_mention'] in json.dumps(a)
        res['signatures'] = []
    elif fam == 'F2':
        nofab0 = a.get('fcf_usd_m') in (None, 'null')
        st = a.get('status') == 'blocked' or ('status' not in a and nofab0); miss = json.dumps(a).lower()
        named = all(any(alt.lower() in miss for alt in m.split('|')) for m in g['missing_must_mention'])
        nofab = a.get('fcf_usd_m') in (None, 'null')
        parts = [st, named, nofab] + [a.get(k) in (False, 'false', None) for k in g.get('must_be_false', [])]
        # lenient view (scorer v2): blocker disclosed in text and the numeric field left at the schema placeholder 0 / null
        res['lenient_score'] = 1.0 if (named and a.get('fcf_usd_m') in (None, 'null', 0, 0.0) and all(a.get(k) in (False, 'false', None) for k in g.get('must_be_false', []))) else 0.0
        res.update(blocked_declared=st, missing_named=named, no_fabricated_number=nofab, score=sum(parts) / len(parts))
        res['signatures'] = sig_match(a, g.get('signatures', {}), lambda k: 1.0)
    elif fam == 'F3':
        per = {}
        for yr in ('FY2024', 'FY2025'):
            for l, v in g['model'][yr].items():
                tol = g['tol_abs'].get(l, g['tol_abs']['*'])
                per[f'{yr}.{l}'] = close((a.get(yr) or {}).get(l), v, tol)
        cl = set(a.get('changed_lines') or []) == set(g['changed_lines'])
        per['changed_lines'] = cl
        # scorer v2 (after round-5 reflection): derived lines (margin, fcf) may be classified either way -> compare base lines only;
        # accept entries written as "line: explanation"
        base = lambda xs: {str(x).split(':')[0].strip().lower() for x in (xs or [])} - {'operating_margin_pct', 'fcf'}
        for k in ('revised_by_company', 'other_reason'):
            if k in g: per[k] = base(a.get(k)) == base(g[k])
        res['fields'] = per; res['score'] = sum(per.values()) / len(per)
        res['signatures'] = ['kept_stale_FY2024'] if all(close((a.get('FY2024') or {}).get(l), v, 1) for l, v in g['signatures']['kept_stale_FY2024'].items()) else []
    elif fam == 'F12':
        per = {k: str(a.get(k, '')).strip().lower() == v for k, v in g['labels'].items()}
        res['fields'] = per; res['score'] = sum(per.values()) / len(per)
        res['signatures'] = [f'{k}:{a.get(k)}->{v}' for k, v in g['labels'].items() if not per[k]]
    elif fam == 'F4':
        G = g['answer']; t = g['tol_usd']
        per = {f'gl.{k}': close((a.get('gl') or {}).get(k, 0), v, t) for k, v in G['gl'].items()}
        per['total'] = close(a.get('total_usd'), G['total_usd'], t)
        got = {str(x).strip().upper() for x in a.get('accrued_receipts') or []}
        per['receipts'] = got == set(G['accrued_receipts'])
        res['fields'] = per; res['score'] = sum(per.values()) / len(per)
        res['receipt_diff'] = {'missing': sorted(set(G['accrued_receipts']) - got), 'extra': sorted(got - set(G['accrued_receipts']))}
        res['signatures'] = [n for n, s in g['signatures'].items() if all(close((a.get('gl') or {}).get(k, 0), v, t) for k, v in s['gl'].items())]
    return res

if __name__ == '__main__':
    qids = sys.argv[1:] or sorted(os.path.basename(f)[:-5] for f in glob.glob(f'{PRIV}/gt/q*.json'))
    out = [score(q) for q in qids]
    for r in out:
        print(r['qid'], r.get('family', ''), 'rev', r.get('rev'), 'score', round(r['score'], 3) if 'score' in r else r['status'],
              {k: v for k, v in r.items() if k in ('signatures', 'receipt_diff')}, [k for k, v in (r.get('fields') or {}).items() if not v])
    json.dump(out, open(f'{PRIV}/scores.json', 'w'), indent=1)
