"""Step 1: apply three transformation operators to one SecQue seed per company.

Operators (each GT is constructed by code from XBRL facts, never written by hand):
  trend   - multi-period tracking (Fin-RATE LT-QA; Finance Agent Benchmark 'Trends')
  missing - missing-premise identification (RealFin; FinanceQA assumption; FailSafeQA missing context)
  verify  - calculation verification, one clean control + one injected error (FinDVer; FinVerBench; FinED-Bench)

Every item carries GT-credibility checks (see step1/REPORT.md section 3).
Usage: python3 -I scripts/make_ops.py   (needs data/secque_full/*.jsonl)
"""
import json, os, re, sys, math, itertools
sys.path.insert(0, os.path.dirname(__file__))
from xbrl_series import value, anniversaries

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SEEDQ = os.path.join(ROOT, '..', 'data', 'secque_full')
OUT = os.path.join(ROOT, 'step1')

def load_seed_rows():
    rows = {}
    for f in ['Ratio', 'Comparison', 'Analysis']:
        for l in open(os.path.join(SEEDQ, f'SECQUE_benchmark_{f}.jsonl')):
            r = json.loads(l); rows[r['QID']] = r
    return rows

# ---------- computation ----------
SEED_ACCNS = set()

def pick(v, which):
    """first = as originally reported; latest = most recent filing; seed = as shown in the seed filing (falls back to first)."""
    if which == 'seed':
        for val, accns in v['values'].items():
            if SEED_ACCNS & set(accns): return float(val)
        return v['first']
    return v[which]

def fetch(s, name, end, which='first'):
    spec = s['items'][name]
    concepts = [c for c in spec if isinstance(c, str) and not c.startswith('USD')]
    unit = next((c for c in spec if isinstance(c, str) and c.startswith('USD')), None)
    months = spec[2] if len(spec) > 2 else s['months']
    for c in concepts:
        v = value(s['cik'], c, end, months, unit)
        if v: return v
    return None

def compute(s, end, which='first'):
    """Return (value, inputs) for the period ending `end`; which='first' (as originally reported) or 'latest'."""
    V, inputs = {}, {}
    m = re.match(r'growth\((\w+)\)', s['expr'])
    names = list(s['items'])
    for n in names:
        v = fetch(s, n, end)
        if v is None: return None, inputs
        V[n] = pick(v, which); inputs[n] = dict(v, used=V[n])
        if m:
            prev = anniversaries(v['end'], 2)[0]
            p = fetch(s, n, prev)
            if p is None: return None, inputs
            # growth must compare like with like: take the base from the same filing as the current value when it is shown there
            same = v['first_accn'] if which == 'first' else v['latest_accn'] if which == 'latest' else None
            pv = next((float(k) for k, a in p['values'].items() if same in a), None) if same else None
            V[n + '_prev'] = pv if pv is not None else pick(p, which)
            inputs[n + '_prev'] = dict(p, used=V[n + '_prev'], base_from_same_filing=pv is not None)
    if m:
        n = m.group(1); val = (V[n] / V[n + '_prev'] - 1) * 100
    else:
        val = eval(s['expr'], {}, V)
        if s['fmt'].startswith('m'): val = val / 1e6
    return val, inputs

def fmt(s, v):
    f = s['fmt']; d = int(f[1:])
    if f[0] == 'x': return f'{v:.{d}f}x'
    if f[0] == 'p': return f'{v:.{d}f}%'
    return f'${v:,.{d}f} million'

def near_boundary(s, v):
    d = int(s['fmt'][1:]); x = abs(v) * 10 ** d
    return abs((x - math.floor(x)) - 0.5) < 0.05

def period_label(s, end):
    return {12: f'fiscal year ended {end}', 3: f'three months ended {end}', 6: f'six months ended {end}', 0: f'as of {end}'}[s['months']]

# ---------- number search in seed context ----------
NUM = re.compile(r'\(?-?\$?\d[\d,]*\.?\d*\)?')
def renderings(val, unit_hint=None):
    """String forms a reported figure may take in a filing table."""
    out = set()
    if abs(val) < 1000:  # per-share
        out |= {f'{abs(val):.2f}'}
        return out
    for scale in (1e6, 1e3):
        x = abs(val) / scale
        for d in (0, 1, 2):
            if abs(round(x, d) - x) < 1e-9 or d == 0 and abs(x - round(x)) < 0.5:
                out.add(f'{x:,.{d}f}')
    return {o for o in out if len(o.replace(',', '').replace('.', '')) >= 3}

def find_lines(ctx, val):
    pats = [re.compile(r'(?<![\d.,])' + re.escape(r) + r'(?![\d]|,\d|\.\d)') for r in renderings(val)]
    return [i for i, line in enumerate(ctx.split('\n')) if any(p.search(line) for p in pats)], renderings(val)

def numbers_in(text):
    out = []
    for t in re.findall(r'\d[\d,]*\.?\d*', text):
        try: out.append(float(t.replace(',', '')))
        except ValueError: pass
    return out

# ---------- operators ----------
def op_trend(s, seed_end):
    ends = anniversaries(seed_end, 5)
    rows = []
    for e in ends:
        v1, inp = compute(s, e, 'first'); v2, _ = compute(s, e, 'latest')
        if v1 is None: return None
        rows.append(dict(end=inp[next(iter(inp))]['end'], first=v1, latest=v2,
                         restated=any(x['restated'] for x in inp.values()),
                         accns=sorted({x['first_accn'] for x in inp.values()})))
    def summary(key):
        vals = [r[key] for r in rows]
        rd = [round(v, int(s['fmt'][1:])) for v in vals]
        top = max(range(len(rd)), key=lambda i: rd[i])
        ties = [i for i in range(len(rd)) if rd[i] == rd[top]]
        rising = all(rd[i + 1] > rd[i] for i in range(len(rd) - 1))
        return dict(values=[fmt(s, v) for v in vals], highest=[rows[i]['end'] for i in ties], rose_every_period=rising)
    a, b = summary('first'), summary('latest')
    unit = {12: 'fiscal years', 3: 'quarters (three-month periods)', 6: 'six-month periods', 0: 'period-end dates'}[s['months']]
    q = (f"For {s['company']}, what was the {s['metric']} ({s['basis']}) for each of the five {unit} ending "
         f"{', '.join(r['end'] for r in rows)}? For each period, use the figures in the 10-K/10-Q that first reported it"
         f"{' (for growth rates, the prior-year comparative shown in that same filing)' if s['kind'] == 'growth' else ''}. "
         f"Which period had the highest value, and did the metric increase in every consecutive period?")
    checks = dict(
        any_restated=any(r['restated'] for r in rows),
        conclusion_stable_under_restatement=(a['highest'] == b['highest'] and a['rose_every_period'] == b['rose_every_period']),
        values_changed_by_restatement=a['values'] != b['values'],
        tie_for_highest=len(a['highest']) > 1,
        rounding_boundary=[r['end'] for r in rows if near_boundary(s, r['first'])],
        n_source_filings=len({x for r in rows for x in r['accns']}))
    return dict(op='trend', question=q, answer=a, answer_if_latest_restated=b, periods=rows, checks=checks)

def op_missing(s, seed, seed_end):
    ctx = seed['context_markdown_with_headers']
    _, inp = compute(s, seed_end, 'seed')
    # remove the denominator (last item) for ratios; the prior-period base for growth; the only item for levels
    names = list(inp)
    target = names[-1] if s['kind'] != 'growth' else [n for n in names if n.endswith('_prev')][0]
    if s['kind'] == 'level' and len(names) > 1: target = names[-1]
    order = [target] + [n for n in reversed(names) if n != target]
    for target in order:
        tv = inp[target]['used']
        idx, forms = find_lines(ctx, tv)
        if idx: break
    if not idx:
        return dict(op='missing', skipped=f'{target} ({tv}) not found in the seed excerpts in forms {sorted(forms)}')
    lines = ctx.split('\n')
    removed = [lines[i] for i in idx]
    pats = [re.compile(r'\(?\$?\s?(?<![\d.,])' + re.escape(r) + r'(?![\d]|,\d|\.\d)\)?') for r in forms]
    for i in idx:  # blank only the cell(s) holding the target figure; the row label and other periods stay
        for pt in pats: lines[i] = pt.sub('', lines[i])
    new_ctx = '\n'.join(lines)
    still, _ = find_lines(new_ctx, tv)
    # derivability: could the removed figure be rebuilt as a sum/difference of two remaining figures?
    nums = sorted(set(n for n in numbers_in(new_ctx) if n >= 10))
    target_scaled = [abs(tv) / sc for sc in (1e6, 1e3)] if abs(tv) >= 1000 else [abs(tv)]
    deriv = []
    S = set(nums)
    for t in target_scaled:
        for a in nums:
            if a >= t: break
            b = round(t - a, 2)
            if b in S or round(b) in S: deriv.append(f'{a:g} + {b:g} = {t:g}')
            if len(deriv) >= 3: break
        for a in nums:
            b = round(a - t, 2)
            if b > 0 and (b in S): deriv.append(f'{a:g} - {b:g} = {t:g}')
            if len(deriv) >= 6: break
    cells = [c.strip() for c in removed[0].split('|') if c.strip()]
    row = cells[1] if len(cells) > 1 and re.fullmatch(r'\d+', cells[0]) else (cells[0] if cells else inp[target]['concept'])
    label = f"{row} for the period ending {inp[target]['end']} (XBRL {inp[target]['concept']})"
    q = (f"Using only the filing excerpts provided, what was {s['company']}'s {s['metric']} ({s['basis']}) "
         f"for the {period_label(s, seed_end)}?")
    return dict(op='missing', question=q, context_modified=new_ctx,
                answer=dict(answerable=False, missing_item=label,
                            expected='State that the figure cannot be computed from the excerpts because this item is missing; do not supply an estimated or recalled number.'),
                removed_from_lines=[l[:200] for l in removed], removed_renderings=sorted(forms),
                checks=dict(removed_value_absent=not still, n_cells_blanked_lines=len(idx),
                            possibly_derivable_from_remaining=deriv[:6]))

def op_verify(s, seed, seed_end):
    ctx = seed['context_markdown_with_headers']
    v, inp = compute(s, seed_end, 'seed')
    names = [n for n in inp if not n.endswith('_prev')]
    out = []
    shown = {n: inp[n]['used'] for n in inp}
    def show(vals):
        parts = []
        for n, x in vals.items():
            parts.append(f"{n}={x:,.2f}" if abs(x) < 1000 else f"{n}=${x/1e6:,.1f}m")
        return '; '.join(parts)
    present = {n: bool(find_lines(ctx, inp[n]['used'])[0]) for n in inp}
    # control
    out.append(dict(op='verify', variant='control', claim_value=fmt(s, v), claim_inputs=show(shown),
                    answer=dict(correct=True, correct_value=fmt(s, v))))
    # injected error: period mismatch if a prior period is available for one input, else arithmetic slip
    err = None
    if s['kind'] != 'growth' and len(names) >= 2:
        n = names[-1]; prev_end = anniversaries(inp[n]['end'], 2)[0]
        p = fetch(s, n, prev_end)
        if p and pick(p, 'seed') != inp[n]['used'] and find_lines(ctx, pick(p, 'seed'))[0]:
            V = dict(shown); V[n] = pick(p, 'seed')
            bad = eval(s['expr'], {}, V) / (1e6 if s['fmt'].startswith('m') else 1)
        if p and 'bad' in dir() and abs(bad - v) >= 3 * 10 ** -int(s['fmt'][1:]) and abs(bad - v) >= 0.02 * abs(v):
            err = dict(type='period_mismatch', detail=f"{n} taken from the period ending {p['end']} instead of {inp[n]['end']}",
                       claim_value=fmt(s, bad), claim_inputs=show(V), wrong_input_in_excerpts=bool(find_lines(ctx, pick(p, 'seed'))[0]))
    d = int(s['fmt'][1:])
    if err is None:  # transcription error: two adjacent digits of one input swapped (FinanceReasoning: 'extracting wrong numbers')
        for n in sorted(shown, key=lambda k: -len(f"{abs(shown[k]):.0f}")):
            x = shown[n]; scale = 1e5 if abs(x) >= 1000 else 0.01   # digits visible in the claim ($0.1m or $0.01/share)
            digits = f"{abs(x)/scale:.0f}"
            for i in reversed(range(len(digits) - 1)):
                if digits[i] == digits[i + 1]: continue
                sw = digits[:i] + digits[i + 1] + digits[i] + digits[i + 2:]
                V = dict(shown); V[n] = math.copysign(int(sw) * scale, x)
                if '_prev' in n or any(k.endswith('_prev') for k in V):
                    base = n.replace('_prev', '')
                    bad = (V[base] / V[base + '_prev'] - 1) * 100
                else:
                    bad = eval(s['expr'], {}, V) / (1e6 if s['fmt'].startswith('m') else 1)
                if abs(bad - v) >= 3 * 10 ** -d and abs(bad - v) >= 0.02 * max(abs(v), 1e-9):
                    u = (lambda z: f"${abs(z)/1e6:,.1f}m") if scale == 1e5 else (lambda z: f"{abs(z):,.2f}")
                    err = dict(type='transcription', detail=f"{n} copied as {u(V[n])} instead of {u(x)} (two digits swapped)",
                               claim_value=fmt(s, bad), claim_inputs=show(V), wrong_input_in_excerpts=bool(find_lines(ctx, V[n])[0]))
                    break
            if err: break
    if err is None:
        bad = v * 1.1 if v >= 0 else v * 0.9
        err = dict(type='arithmetic', detail='result misstated by 10% although inputs are correct',
                   claim_value=fmt(s, bad), claim_inputs=show(shown))
    if fmt(s, v) == err['claim_value']:
        err['type'] += '_INVALID_same_after_rounding'
    out.append(dict(op='verify', variant='injected_error', error_type=err['type'], error_detail=err['detail'],
                    claim_value=err['claim_value'], claim_inputs=err['claim_inputs'],
                    answer=dict(correct=False, error=err['detail'], correct_value=fmt(s, v)),
                    checks=dict(wrong_input_in_excerpts=err.get('wrong_input_in_excerpts'))))
    for o in out:
        o['question'] = (f"An analyst wrote: \"{s['company']}'s {s['metric']} ({s['basis']}) for the {period_label(s, seed_end)} "
                         f"was {o['claim_value']} (inputs: {o['claim_inputs']}).\" Using the filing excerpts provided, "
                         f"is this statement correct? If not, explain what is wrong and give the correct figure.")
        o.setdefault('checks', {})
        o['checks'].update(inputs_found_in_excerpts=present, rounding_boundary=near_boundary(s, v))
    return out

def op_cross(s, seed_end):
    """Cross-company comparison (Fin-RATE EC-QA; Finance Agent Benchmark 'Market Analysis')."""
    pr = s.get('peer')
    if not pr: return None
    s2 = dict(s, company=pr['company'], cik=pr['cik'], items=pr.get('items', s['items']))
    va, ia = compute(s, seed_end, 'first'); vb, ib = compute(s2, pr['end'], 'first')
    if va is None or vb is None:
        return dict(op='cross', skipped=f"peer value unavailable for {pr['company']}")
    ea = ia[next(iter(ia))]['end']; eb = ib[next(iter(ib))]['end']
    d = int(s['fmt'][1:])
    ra, rb = round(va, d), round(vb, d)
    unit = 'percentage points' if s['fmt'][0] == 'p' else ('times' if s['fmt'][0] == 'x' else '$ million')
    q = (f"Compare the {s['metric']} ({s['basis']}) of {s['company']} for the {period_label(s, ea)} with that of "
         f"{pr['company']} for the {period_label(s, eb)}, each as reported in the company's own filing for that period. "
         f"Which company is higher, and by how much ({unit})?")
    concept_diff = {n: (ia[n]['concept'], ib[n]['concept']) for n in ia if n in ib and ia[n]['concept'] != ib[n]['concept']}
    higher = s['company'] if ra > rb else pr['company'] if rb > ra else 'tie'
    return dict(op='cross', question=q,
                answer=dict(values={s['company']: fmt(s, va), pr['company']: fmt(s, vb)}, higher=higher,
                            difference=f"{abs(ra - rb):.{d}f} {unit}"),
                checks=dict(period_end_gap_days=abs((__import__('datetime').date.fromisoformat(ea) - __import__('datetime').date.fromisoformat(eb)).days),
                            concept_differs_between_companies=concept_diff,
                            restated=any(x['restated'] for x in list(ia.values()) + list(ib.values())),
                            tie_after_rounding=ra == rb,
                            rounding_boundary=near_boundary(s, va) or near_boundary(s, vb),
                            accessions=sorted({x['first_accn'] for x in list(ia.values()) + list(ib.values())})))

# ---------- backtest against the seed GT ----------
def backtest(s, seed, seed_end):
    v, inp = compute(s, seed_end, 'seed')
    v_first, _ = compute(s, seed_end, 'first')
    gt = seed['ground_truth_answer']
    d = int(s['fmt'][1:])
    nums = numbers_in(gt)
    target = v
    hit = [n for n in nums if abs(n - round(abs(target), d)) <= 10 ** -d * 1.01]
    inputs_in_gt = {}
    for n, x in inp.items():
        forms = renderings(x['used'])
        inputs_in_gt[n] = any(f in gt for f in forms)
    return dict(our_value=fmt(s, v), value_if_originally_reported=fmt(s, v_first), seed_gt_contains_value=bool(hit), inputs_in_seed_gt=inputs_in_gt,
                restated_inputs=[n for n, x in inp.items() if x['restated']],
                seed_accession=seed['accession_number'],
                our_accessions=sorted({x['first_accn'] for x in inp.values()}),
                seed_gt_excerpt=gt[:400])

def main():
    rows = load_seed_rows()
    S = json.load(open(os.path.join(OUT, 'seeds.json')))
    items, summary = [], []
    for s in S:
        seed = rows[s['qid']]
        seed_end = s['end']
        SEED_ACCNS.clear(); SEED_ACCNS.update(a.strip() for a in seed['accession_number'].split(';'))
        bt = backtest(s, seed, seed_end)
        tr = op_trend(s, seed_end)
        ms = op_missing(s, seed, seed_end)
        vf = op_verify(s, seed, seed_end)
        cr = op_cross(s, seed_end)
        base = dict(seed_qid=s['qid'], company=s['company'], cik=s['cik'], metric=s['metric'], basis=s['basis'],
                    seed_question=seed['Question'], seed_period_end=seed_end)
        for k, it in enumerate([tr, ms] + vf + [cr]):
            if it is None: continue
            items.append(dict(base, item_id=f"{s['qid']}_{it['op']}{'_'+it.get('variant','') if it['op']=='verify' else ''}", **it))
        summary.append(dict(seed_qid=s['qid'], company=s['company'], metric=s['metric'], backtest=bt,
                            trend_ok=tr is not None, missing_ok='skipped' not in ms, skipped_seeds=s.get('skipped', [])))
        print(f"{s['qid']:9} {s['company'][:24]:24} ours={bt['our_value']:>16} orig={bt['value_if_originally_reported']:>16} seedGT_match={bt['seed_gt_contains_value']!s:5} "
              f"trend={'ok' if tr else '--'} missing={'ok' if 'skipped' not in ms else 'skip'} restated={bt['restated_inputs']}")
    with open(os.path.join(OUT, 'items.jsonl'), 'w') as f:
        for it in items: f.write(json.dumps(it, ensure_ascii=False) + '\n')
    json.dump(summary, open(os.path.join(OUT, 'seed_backtest.json'), 'w'), indent=1, ensure_ascii=False)
    print(len(items), 'items')

if __name__ == '__main__':
    main()
