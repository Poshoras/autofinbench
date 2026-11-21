"""Score model answers on step1/eval. Rule-based main score; an LLM judge only for two free-text sub-scores.

  python3 -I scripts/score_eval.py RESPONSES.jsonl OUT_DIR [JUDGMENTS.jsonl]

RESPONSES.jsonl: one line per item, {"item_id": ..., "response": "<final answer text>"}
  (for reasoning models, the final answer only, not the reasoning trace).
OUT_DIR gets: scores.jsonl, summary.md, failures.csv, judge_requests.jsonl.
JUDGMENTS.jsonl (optional, second pass): {"item_id": ..., "judgment": "<judge reply containing {\"match\": true|false, ...}>"}"""
import json, os, re, sys, csv, math, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
GOLD = os.path.join(ROOT, 'step1', 'eval', 'gold.jsonl')

JUDGE_SYSTEM = "You grade one part of a model's answer against a reference. Reply with one JSON object only."
JUDGE_USER = {
    'missing': ("A question could not be answered because one input is missing from the filing excerpts.\n"
                "Reference missing item: {ref}\n\nModel answer:\n{resp}\n\n"
                "Does the model name the same missing item (any wording; naming the same line item for the same period counts)? "
                'Reply {{"match": true or false, "reason": "<one sentence>"}}'),
    'verify': ("An analyst's statement contains one injected error.\nReference error: {ref}\n\nModel answer:\n{resp}\n\n"
               "Does the model identify the same error, i.e. the same wrong input and the same kind of mistake "
               "(e.g. figure taken from the wrong period, digits transposed)? Any wording counts; finding only that the "
               'result is wrong, without locating the input, does not. Reply {{"match": true or false, "reason": "<one sentence>"}}'),
}

def last_json(text):
    """The last parseable top-level {...} object in the text."""
    text = re.sub(r'```(?:json)?', '', text or '')
    ends = [i for i, ch in enumerate(text) if ch == '}']
    for e in reversed(ends):
        depth = 0
        for b in range(e, -1, -1):
            if text[b] == '}': depth += 1
            elif text[b] == '{':
                depth -= 1
                if depth == 0:
                    try: return json.loads(text[b:e + 1])
                    except Exception: break
    return None

def to_num(x):
    if isinstance(x, bool) or x is None: return None
    if isinstance(x, (int, float)): return float(x)
    s = str(x).replace(',', '').replace('$', '').strip()
    neg = s.startswith('(') and s.endswith(')')
    m = re.search(r'-?\d*\.?\d+', s)
    if not m: return None
    v = float(m.group(0))
    return -abs(v) if neg else v

def to_bool(x):
    if isinstance(x, bool): return x
    if isinstance(x, str) and x.strip().lower() in ('true', 'yes'): return True
    if isinstance(x, str) and x.strip().lower() in ('false', 'no'): return False
    return None

def tol(gt, d): return max(10 ** -d, 0.005 * abs(gt)) + 1e-9

def num_ok(v, gt, g, rng=None):
    """(ok, flag). Tolerance: 1 display unit or 0.5% relative, whichever is larger.
    Unit slips are accepted but flagged: a fraction for a percent (0.514 for 51.4) or raw dollars for $ millions."""
    v = to_num(v)
    if v is None or gt is None: return False, 'no_number'
    if rng and rng[0] - 1e-9 <= v <= rng[1] + 1e-9: return True, ''
    d = g['display_decimals']
    if abs(v - gt) <= tol(gt, d): return True, ''
    if g['unit'] == 'percent' and abs(v * 100 - gt) <= tol(gt, d): return True, 'fraction_form'
    if g['unit'] == 'USD millions' and abs(v / 1e6 - gt) <= tol(gt, d): return True, 'raw_dollars'
    return False, ''

def date_ok(pred, gold_list, period_ends):
    p = str(pred or '').strip()
    if p in gold_list: return True
    years = [e[:4] for e in period_ends]
    y = re.fullmatch(r'(?:FY\s*)?(\d{4})', p)
    return bool(y and years.count(y.group(1)) == 1 and any(g[:4] == y.group(1) for g in gold_list))

def name_ok(pred, gold_name, names):
    def toks(s): return {t for t in re.findall(r'[a-z&]+', s.lower()) if t not in ('inc', 'the', 'co', 'corp', 'corporation', 'company', 'group', 'of', 'and', 'p&g', 'nee')}
    p = toks(str(pred or ''))
    if not p: return False
    best = max(names, key=lambda n: len(p & toks(n)))
    return best == gold_name and len(p & toks(gold_name)) > 0

def score(g, resp):
    j = last_json(resp)
    r = dict(item_id=g['item_id'], op=g['op'], variant=g['variant'], seed_qid=g['seed_qid'], in_main_score=g['in_main_score'],
             parsed=j is not None, correct=False, flags=[], parts={})
    if j is None: r['flags'].append('no_json'); return r, j
    op = g['op']
    if op in ('base', 'reconstruct', 'missing'):
        ans = to_bool(j.get('answerable')); val = j.get('value')
        if g['answerable']:
            ok, fl = num_ok(val, g['value'], g, g.get('accept_range'))
            r['parts'] = dict(answerable=ans is True, value=ok)
            r['correct'] = ans is True and ok
            if ans is False: r['flags'].append('refused_answerable_item')
        else:
            gave_number = to_num(val) is not None
            r['parts'] = dict(answerable=ans is False, no_number=not gave_number)
            r['correct'] = ans is False and not gave_number
            if gave_number: r['flags'].append('gave_number_for_unanswerable_item')
            fl = ''
    elif op == 'trend':
        vals = j.get('values') or []
        oks = [num_ok(v, t, g)[0] for v, t in zip(vals, g['values'])] if isinstance(vals, list) else []
        v_ok = len(oks) == 5 and all(oks)
        h_ok = date_ok(j.get('highest_period_end'), g['highest_period_end'], g['period_ends'])
        i_ok = to_bool(j.get('increased_every_period')) == g['increased_every_period']
        r['parts'] = dict(values=v_ok, n_values_ok=sum(oks), highest=h_ok, increased=i_ok)
        r['correct'] = v_ok and h_ok and i_ok
        alt = g['if_latest_restated']
        if alt['values'] != g['values'] and isinstance(vals, list) and len(vals) == 5 and \
                all(num_ok(v, t, g)[0] for v, t in zip(vals, alt['values'])) and not v_ok:
            r['flags'].append('used_restated_figures')
        fl = ''
    elif op == 'verify':
        sc = to_bool(j.get('statement_correct'))
        if g['statement_correct']:
            r['parts'] = dict(says_correct=sc is True)
            r['correct'] = sc is True
            if sc is False: r['flags'].append('false_alarm')
            fl = ''
        else:
            ok, fl = num_ok(j.get('correct_value'), g['correct_value'], g)
            r['parts'] = dict(detects_error=sc is False, correct_value=ok)
            r['correct'] = sc is False and ok
            if sc is True: r['flags'].append('missed_error')
    elif op == 'cross':
        names = list(g['values']); pv = j.get('values') or {}
        got = {}
        if isinstance(pv, dict):
            for k, v in pv.items():
                m = [n for n in names if name_ok(k, n, names)]
                if m: got[m[0]] = v
        v_ok = all(num_ok(got.get(n), g['values'][n], g)[0] for n in names)
        h_ok = name_ok(j.get('higher'), g['higher'], names)
        dg = dict(g, unit='pp' if g['unit'] == 'percent' else g['unit'])
        d_ok = num_ok(abs(to_num(j.get('difference')) or 0) if to_num(j.get('difference')) is not None else None, g['difference'], dg)[0]
        r['parts'] = dict(values=v_ok, higher=h_ok, difference=d_ok)
        r['correct'] = v_ok and h_ok and d_ok
        fl = ''
    if fl: r['flags'].append(fl)
    return r, j

def wilson(k, n):
    if n == 0: return (float('nan'),) * 2
    z = 1.96; p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0, c - h), min(1, c + h)

def main(resp_path, out_dir, judg_path=None):
    os.makedirs(out_dir, exist_ok=True)
    gold = {g['item_id']: g for g in (json.loads(l) for l in open(GOLD))}
    resp = {}
    for l in open(resp_path):
        d = json.loads(l); resp[d['item_id']] = d.get('response', '')
    judg = {}
    if judg_path:
        for l in open(judg_path):
            d = json.loads(l); jj = last_json(d.get('judgment', '')); judg[d['item_id']] = to_bool((jj or {}).get('match'))
    rows, jreq = [], []
    for iid, g in gold.items():
        if iid not in resp:
            rows.append(dict(item_id=iid, op=g['op'], variant=g['variant'], seed_qid=g['seed_qid'], in_main_score=g['in_main_score'],
                             parsed=False, correct=False, flags=['no_response'], parts={})); continue
        r, j = score(g, resp[iid])
        kind = 'missing' if g['op'] == 'missing' else 'verify' if (g['op'] == 'verify' and not g['statement_correct']) else None
        if kind:
            ref = g['missing_item'] if kind == 'missing' else g['error']
            jreq.append(dict(item_id=iid, system=JUDGE_SYSTEM, user=JUDGE_USER[kind].format(ref=ref, resp=resp[iid][-3000:])))
            r['judge_match'] = judg.get(iid)
        r['final_json'] = j
        rows.append(r)
    with open(os.path.join(out_dir, 'scores.jsonl'), 'w') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(os.path.join(out_dir, 'judge_requests.jsonl'), 'w') as f:
        for q in jreq: f.write(json.dumps(q, ensure_ascii=False) + '\n')
    # ---- summary ----
    M = [r for r in rows if r['in_main_score']]
    L = ['# Scores', '', f'responses: {len(resp)} / {len(gold)} items; no JSON parsed: {sum(1 for r in rows if not r["parsed"])}', '',
         '## Accuracy by operator (main score, rule-based)', '', '| operator | n | correct | accuracy | 95% CI |', '|---|---|---|---|---|']
    def key(r): return r['op'] + (f" ({r['variant']})" if r['variant'] else '')
    groups = collections.OrderedDict()
    for k in ['base', 'trend', 'cross', 'missing', 'reconstruct', 'verify (control)', 'verify (injected_error)']: groups[k] = []
    for r in M: groups.setdefault(key(r), []).append(r)
    for k, rs in groups.items():
        n = len(rs); c = sum(r['correct'] for r in rs); lo, hi = wilson(c, n)
        L.append(f'| {k} | {n} | {c} | {c / n:.0%} | {lo:.0%}–{hi:.0%} |' if n else f'| {k} | 0 | – | – | – |')
    base = {r['seed_qid']: r['correct'] for r in M if r['op'] == 'base'}
    L += ['', '## Paired with the base item of the same seed', '',
          '| operator | pairs | base right | operator right | base right, operator wrong | base wrong, operator right |', '|---|---|---|---|---|---|']
    for k, rs in groups.items():
        if k == 'base': continue
        ps = [(base[r['seed_qid']], r['correct']) for r in rs if r['seed_qid'] in base]
        if ps: L.append(f'| {k} | {len(ps)} | {sum(a for a, _ in ps)} | {sum(b for _, b in ps)} | {sum(a and not b for a, b in ps)} | {sum(b and not a for a, b in ps)} |')
    ver = {}
    for r in M:
        if r['op'] == 'verify': ver.setdefault(r['seed_qid'], {})[r['variant']] = r['correct']
    pair_ok = sum(1 for v in ver.values() if v.get('control') and v.get('injected_error'))
    fl = collections.Counter(f for r in rows for f in r['flags'])
    L += ['', '## Diagnostics', '',
          f'- verify pairs with both control and injected item right: {pair_ok} / {len(ver)}',
          f'- flags: ' + (', '.join(f'{k} {v}' for k, v in fl.most_common()) or 'none')]
    for op in ('trend', 'cross'):
        rs = [r for r in M if r['op'] == op and r['parsed']]
        if rs:
            parts = collections.Counter(p for r in rs for p, ok in r['parts'].items() if ok is True)
            L.append(f'- {op} sub-scores: ' + ', '.join(f'{p} {parts[p]}/{len(rs)}' for p in rs[0]['parts'] if isinstance(rs[0]['parts'][p], bool)))
    jr = [r for r in M if 'judge_match' in r]
    if any(r['judge_match'] is not None for r in jr):
        for op in ('missing', 'verify'):
            rs = [r for r in jr if r['op'] == op and r['judge_match'] is not None]
            if rs: L.append(f'- judge, {op}: names the right {"missing item" if op == "missing" else "error"} in {sum(r["judge_match"] for r in rs)}/{len(rs)}')
    else:
        L.append(f'- judge sub-scores pending: send {len(jreq)} requests in judge_requests.jsonl, then re-run with the judgments file')
    nm = [r for r in rows if not r['in_main_score']]
    for r in nm: L.append(f"- not in main score: {r['item_id']} correct={r['correct']} flags={r['flags']}")
    open(os.path.join(out_dir, 'summary.md'), 'w').write('\n'.join(L) + '\n')
    with open(os.path.join(out_dir, 'failures.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['item_id', 'op', 'variant', 'parts', 'flags', 'model_json', 'gold', 'triage (model_error / item_problem / unclear)'])
        for r in rows:
            if r['correct']: continue
            g = gold[r['item_id']]
            gk = {k: g[k] for k in g if k in ('answerable', 'value_display', 'missing_item', 'values_display', 'highest_period_end',
                                             'increased_every_period', 'statement_correct', 'correct_value_display', 'error', 'higher', 'difference')}
            w.writerow([r['item_id'], r['op'], r['variant'] or '', json.dumps(r['parts']), ' '.join(r['flags']),
                        json.dumps(r.get('final_json'), ensure_ascii=False), json.dumps(gk, ensure_ascii=False), ''])
    print('\n'.join(L))

if __name__ == '__main__':
    main(*sys.argv[1:])
