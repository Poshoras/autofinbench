"""Simulated AutoFinBench agent (pre-experiment, group C).

Judgment steps (pattern learning, planning decision, question writing, review verdict) are
authored in step0/specs/<QID>.json. This runner executes the deterministic tool steps around them:

  1 learn pattern  -> locate every number of the seed GT in the seed's own context pages
  2 backtest       -> re-derive seed inputs from the seed filing's XBRL, re-compute seed answers,
                      auto-diagnose mismatching inputs (which XBRL concept does the seed number really match?)
  3 plan           -> check every required item is available in the target filing
  4 compute        -> compute the new answers from the target filing's XBRL
  5 write question -> render question + structured answer (values filled from step 4, never typed by hand)
  6 review         -> independent text check: every input value must appear in the target filing's
                      primary document text; answer-leak check; plus the authored review verdict

Usage: python3 -I scripts/run_agent.py [QID ...]   (default: all specs)
Outputs: step0/runs/<QID>.json, step0/new_benchmark_agent.csv
"""
import sys, os, json, re, csv, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edgar, xbrl_instance as XI, doctext

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STEP0 = os.path.join(REPO, 'step0')
TOK = re.compile(r'([A-Za-z_]\w*)@(\w+)')
csv.field_size_limit(10**9)


def num(s):
    return float(str(s).replace(',', '').replace('$', '').replace('%', '').strip())


def decimals_of(s):
    s = str(s).replace(',', '')
    return len(s.split('.')[1]) if '.' in s else 0


def disp(item, val):
    """XBRL raw value -> display units used in filings / GT (USD millions unless scale='unit')."""
    return val if item.get('scale') == 'unit' else val / 1e6


# ---------------------------------------------------------------- metric expansion / evaluation
def expand(spec, side):
    labels = list(spec['periods'][side])
    out = {}
    for name, tmpl in spec['metrics'].items():
        for p in spec['metric_periods'][side]:
            i = labels.index(p)
            prev = labels[i - 1] if i > 0 else None
            if '{prev}' in tmpl and prev is None:
                continue
            out[f'{name}@{p}'] = tmpl.replace('{p}', p).replace('{prev}', prev or '')
    return out


def evaluate(expr, V):
    missing = [m.group(0) for m in TOK.finditer(expr) if m.group(0) not in V]
    if missing:
        return None, missing
    py = TOK.sub(lambda m: f'V["{m.group(0)}"]', expr)
    try:
        return eval(py, {'__builtins__': {}}, {'V': V}), []
    except ZeroDivisionError:
        return None, ['division by zero']


def needed_keys(exprs):
    return sorted({m.group(0) for e in exprs for m in TOK.finditer(e)})


CUTOFF = '2026-01-01'   # step0 triage: company must have a 10-K/10-Q filed on/after this date
_TEXT = {}


def ftext(cik, accn):
    if accn not in _TEXT:
        _TEXT[accn] = doctext.text(cik, accn)
    return _TEXT[accn]


def load_spec(qid):
    spec = json.load(open(os.path.join(STEP0, 'specs', f'{qid}.json'), encoding='utf-8'))
    if 'profile' in spec:   # shared per-filing setup: company, seed/target filings, periods, data items
        prof = json.load(open(os.path.join(STEP0, 'profiles', spec['profile'] + '.json'), encoding='utf-8'))
        spec = {**prof, **spec, 'items': {**prof.get('items', {}), **spec.get('items', {})}}
    return spec


def relabel(obj, lm):
    """Replace period labels (e.g. FY2026 -> FY2024) in every string / key of a nested structure."""
    if not lm:
        return obj
    rx = re.compile(r'\b(' + '|'.join(map(re.escape, sorted(lm, key=len, reverse=True))) + r')\b')
    if isinstance(obj, str):
        return rx.sub(lambda m: lm[m.group(1)], obj)
    if isinstance(obj, list):
        return [relabel(x, lm) for x in obj]
    if isinstance(obj, dict):
        return {relabel(k, lm): relabel(v, lm) for k, v in obj.items()}
    return obj


def lookup(doc, spec, side, key):
    """Value of item@period. Sources: XBRL (default) or filing text (item.source == 'text').
    A period may carry its own 'accn' (e.g. prior-year balances taken from an older 10-K)."""
    item_name, label = key.split('@')
    item = spec['items'][item_name]
    per = spec['periods'][side][label]
    accn = per.get('accn') or spec[f'{side}_accn']
    if item.get('source') == 'text':
        rx = item.get(f'text_regex_{side}', {}).get(label)
        if not rx:
            return None
        accn = rx.get('accn') or accn
        m = re.search(rx['pattern'], ftext(spec['cik'], accn))
        if not m:
            return None
        val = num(m.group(rx.get('group', 1)))
        return dict(concept='TEXT', accn=accn, dims={}, raw=val, value=val * item.get('sign', 1), text_match=m.group(0)[:200])
    if per.get('accn'):
        doc = XI.load(spec['cik'], per['accn'])
    concepts = item.get(f'concepts_{side}', item.get('concepts', []))
    dims = item.get(f'dims_{side}', item.get('dims', {}))
    for c in concepts:
        if item['type'] == 'instant':
            f = XI.query(doc, c, end=per['end'], dims=dims)
        else:
            f = XI.query(doc, c, end=per['end'], start=per.get('start'), dims=dims) if per.get('start') else None
        if f:
            return dict(concept=c, accn=accn, dims=dims, raw=f['val'], value=disp(item, f['val']) * item.get('sign', 1))
    return None


# ---------------------------------------------------------------- step 1: locate seed numbers in context
def split_pages(ctx):
    parts = re.split(r'(page \d+):', ctx)
    pages, cur = [], ('?', parts[0])
    pages.append(cur)
    for i in range(1, len(parts) - 1, 2):
        pages.append((parts[i].split()[1], parts[i + 1]))
    return pages


def locate(ctx, s):
    pat = re.compile(r'(?<![\d,.])' + re.escape(s) + r'(?![\d])')
    hits = []
    for pg, body in split_pages(ctx):
        for line in body.split('\n'):
            if pat.search(line):
                cells = [c.strip() for c in line.split('|') if c.strip()]
                label = next((c for c in cells if re.search(r'[A-Za-z]{3}', c)), line.strip()[:80])
                hits.append({'page': pg, 'row_label': label[:90]})
    return hits[:3]


def diagnose(doc, spec, key, target_val):
    """Which non-dimensional XBRL concept in the seed filing has this value for this period?"""
    item_name, label = key.split('@')
    item = spec['items'][item_name]
    per = spec['periods']['seed'][label]
    out = []
    for f in doc['facts']:
        if f['dims']:
            continue
        same_period = (f.get('instant') == per['end']) if item['type'] == 'instant' else \
                      (f.get('start') == per.get('start') and f.get('end') == per['end'])
        if same_period and abs(disp(item, abs(f['val'])) - abs(target_val)) < 0.5:
            out.append(f['concept'])
    return sorted(set(out))


# ---------------------------------------------------------------- main per-question run
def run(qid, seed_rows):
    spec = load_spec(qid)
    seed = seed_rows[qid]
    traj = {'qid': qid, 'seed': {'question': seed['Question'].strip(), 'ground_truth_answer': seed['ground_truth_answer'],
                                 'accession_number': seed['accession_number'], 'page_number': seed['page_number']}}
    cik = spec['cik']

    # ---- step 0: triage (company-level rule, no judgment needed)
    latest = max((f['filed'] for f in edgar.filings(cik)), default=None)
    traj['step0_triage'] = {'latest_10K_10Q_filed': latest, 'cutoff': CUTOFF, 'pass': bool(latest and latest >= CUTOFF)}
    if not traj['step0_triage']['pass'] and 'step1_pattern' not in spec:
        traj['final_status'] = 'REJECTED'
        traj['reject_reason'] = (f'批量淘汰（step0 规则）：{spec["company"]} 最新一份 10-K/10-Q 提交于 {latest}，'
                                 f'早于 {CUTOFF}，没有知识截止日之后的新数据')
        return traj, None

    # ---- step 1
    ctx = seed['context_markdown_with_headers']
    located = {k: locate(ctx, v) for k, v in {**spec['step1_pattern'].get('seed_numbers', {}),
                                              **spec['step1_pattern'].get('seed_answers', {})}.items()}
    traj['step1_learn_pattern'] = {**spec['step1_pattern'],
                                   'data_items': {k: {f: v[f] for f in ('label', 'statement', 'type') if f in v} for k, v in spec['items'].items()},
                                   'formulas': spec['metrics'], 'evidence_in_seed_context': located}

    # ---- step 2
    sdoc = XI.load(cik, spec['seed_accn'])
    seed_metrics = expand(spec, 'seed')
    keys = sorted(set(needed_keys(seed_metrics.values())) | set(spec['step1_pattern'].get('seed_numbers', {})))
    xb = {k: lookup(sdoc, spec, 'seed', k) for k in keys}
    stated = {k: num(v) for k, v in spec['step1_pattern'].get('seed_numbers', {}).items()}
    inputs = []
    for k in keys:
        x, s = xb[k], stated.get(k)
        if x is None and s is None:
            status = 'MISSING'
        elif x is None:
            status = 'NO_XBRL (context only)' if located.get(k) else 'NO_XBRL_AND_NOT_IN_CONTEXT'
        elif s is None:
            status = 'XBRL_ONLY'
        else:
            status = 'MATCH' if abs(x['value'] - s) < 0.5 * 10 ** -decimals_of(spec['step1_pattern']['seed_numbers'][k]) + 1e-9 else 'SEED_INPUT_MISMATCH'
        row = {'key': k, 'seed_stated': s, 'xbrl': x['value'] if x else None, 'xbrl_concept': x['concept'] if x else None, 'status': status}
        if status == 'SEED_INPUT_MISMATCH':
            row['diagnosis_seed_value_matches_concept'] = diagnose(sdoc, spec, k, s)
        inputs.append(row)
    V_verified = {k: (xb[k]['value'] if xb[k] else stated.get(k)) for k in keys if (xb[k] or k in stated)}
    V_stated = {**V_verified, **stated}
    answers = []
    for mk, expr in seed_metrics.items():
        sa = spec['step1_pattern'].get('seed_answers', {}).get(mk)
        v_st, _ = evaluate(expr, V_stated)
        v_ok, miss = evaluate(expr, V_verified)
        row = {'metric': mk, 'formula': expr, 'seed_answer': sa,
               'recomputed_from_seed_inputs': v_st, 'recomputed_from_filing': v_ok, 'missing': miss}
        if sa is not None:
            d = decimals_of(sa)
            row['arithmetic_ok'] = v_st is not None and round(v_st, d) == round(num(sa), d)
            row['filing_ok'] = v_ok is not None and round(v_ok, d) == round(num(sa), d)
            row['corrected_seed_answer'] = round(v_ok, d) if v_ok is not None else None
            row['within_1_unit'] = v_ok is not None and abs(v_ok - num(sa)) <= 10 ** -d + 1e-9
        answers.append(row)
    # exception-based: only substantive mismatches need judgment; rounding-level ones are just recorded
    flags = [r['key'] for r in inputs if r['status'] == 'SEED_INPUT_MISMATCH'] + \
            [a['metric'] for a in answers if a.get('seed_answer') is not None and not a['within_1_unit']]
    rounding_only = [a['metric'] for a in answers if a.get('seed_answer') is not None and not a['filing_ok'] and a['within_1_unit']]
    verdict = spec.get('step2_verdict', 'auto')
    if verdict == 'auto':
        verdict = 'MATCH' if not flags else '不吻合，需判断：' + ', '.join(flags)
        if rounding_only:
            verdict += f'（另有舍入级差异：{", ".join(rounding_only)}）'
    traj['step2_backtest'] = {'seed_filing': spec['seed_accn'], 'inputs': inputs, 'answers': answers,
                              'flags_for_attention': flags, 'rounding_level_differences': rounding_only, 'verdict': verdict}

    # ---- step 3
    plan = dict(spec['step3_plan'])
    target_meta = None
    if spec.get('target_accn'):
        target_meta = next(f for f in edgar.filings(cik) if f['accn'] == spec['target_accn'])
        tdoc = XI.load(cik, spec['target_accn'])
        tmetrics = expand(spec, 'target')
        # alternative reasonable definitions (graded as also-correct); overrides by metric name or by metric@period
        vmetrics = {}
        for vn, ov in spec.get('step5_question', {}).get('variants', {}).items():
            vm = expand({**spec, 'metrics': {**spec['metrics'], **{k: v for k, v in ov.items() if '@' not in k}}}, 'target')
            vm.update({k: v for k, v in ov.items() if '@' in k})
            vmetrics[vn] = vm
        tkeys = needed_keys(list(tmetrics.values()) + [e for vm in vmetrics.values() for e in vm.values()])
        txb = {k: lookup(tdoc, spec, 'target', k) for k in tkeys}
        plan['target_filing'] = target_meta
        plan['availability'] = {k: (txb[k]['concept'] if txb[k] else 'MISSING') for k in tkeys}
    traj['step3_plan'] = plan

    if plan['decision'] != 'shift':
        traj['final_status'] = 'REJECTED'
        traj['reject_reason'] = plan['rationale']
        traj['revisions'] = spec.get('revisions', [])
        return traj, None

    # ---- step 4
    TV = {k: v['value'] for k, v in txb.items() if v}

    def compute(mset):
        out = {}
        for mk, expr in mset.items():
            v, miss = evaluate(expr, TV)
            out[mk] = {'formula': expr, 'value': v, 'missing': miss}
        return out
    results = compute(tmetrics)
    vresults = {vn: compute(vm) for vn, vm in vmetrics.items()}
    traj['step4_compute'] = {'inputs': {k: (v and {'concept': v['concept'], 'dims': v['dims'], 'value': v['value']}) for k, v in txb.items()},
                             'metrics': results, 'variant_metrics': vresults}

    # ---- step 5: paired questions (old period / new period) that differ ONLY in time,
    #      each self-contained (company, period, required metrics, units, key basis); GT generated by code
    q5 = spec['step5_question']
    lm = spec.get('label_map', {})            # target period label -> seed period label
    q5_old = relabel(q5, lm)
    question_old = q5.get('old_question', traj['seed']['question'])
    tm = q5.get('time_map', {})
    if tm:
        rx = re.compile('|'.join(re.escape(k) for k in sorted(tm, key=len, reverse=True)))
        question = rx.sub(lambda m: tm[m.group(0)], question_old)
    else:
        question = question_old

    def make_answer(q, res):
        ans = {}
        for mk, d in q['answer_decimals'].items():
            ans[mk] = round(res[mk]['value'], d) if d > 0 else round(res[mk]['value'])
        for name, (metric, a, b) in q.get('directions', {}).items():
            va, vb = ans[f'{metric}@{a}'], ans[f'{metric}@{b}']
            ans[name] = 'increased' if vb > va else ('decreased' if vb < va else 'unchanged')
        for name, (op, keys_) in q.get('selectors', {}).items():
            vals = {k: res[k]['value'] for k in keys_}
            best = (max if op == 'argmax' else min)(vals, key=vals.get).split('@')[0]
            ans[name] = q.get('selector_labels', {}).get(best, best)
        for name, (a, op, b) in q.get('comparisons', {}).items():
            ans[name] = 'yes' if {'>': res[a]['value'] > res[b]['value'], '<': res[a]['value'] < res[b]['value']}[op] else 'no'
        return ans

    def fmt(q, k, v):
        base, per = k.split('@')[0], (k.split('@')[1] if '@' in k else '')
        lab = q.get('display_names', {}).get(base, base) + (f' ({per})' if per else '')
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return f"{lab}: {v:,.{q['answer_decimals'].get(k, 0)}f}"
        return f'{lab}: {v}'

    def item_text(key, v):
        item = spec['items'][key.split('@')[0]]
        if item.get('scale') == 'unit':
            return f'{v:,.2f}' if v != int(v) else f'{v:,.0f}'
        return f'{v:,.0f}'

    def gt_text(q, ans, res, V):
        """Ground truth = the required answers + the calculation with the actual numbers + the data used."""
        out = ['Answer:'] + ['- ' + fmt(q, k, v) for k, v in ans.items()] + ['Calculation:']
        for k in q['answer_decimals']:
            shown = TOK.sub(lambda m: item_text(m.group(0), V[m.group(0)]), res[k]['formula']).replace('*', 'x')
            out.append(f"- {fmt(q, k, ans[k])}  [{shown}]")
        out.append('Data used ($ millions unless stated):')
        for key in needed_keys([res[k]['formula'] for k in q['answer_decimals']]):
            out.append(f"- {spec['items'][key.split('@')[0]]['label']} ({key.split('@')[1]}): {item_text(key, V[key])}")
        return '\n'.join(out)

    ans = make_answer(q5, results)
    variants_ans = {}
    for vn, vres in vresults.items():
        va = make_answer(q5, vres)
        variants_ans[vn] = {k: v for k, v in va.items() if ans.get(k) != v}
    gt = gt_text(q5, ans, results, TV)
    if any(variants_ans.values()):
        gt += '\nAlternative basis (accepted only if applied consistently to ALL items): ' + ' | '.join(
            f'{vn}: ' + '; '.join(fmt(q5, k, v) for k, v in d.items()) for vn, d in variants_ans.items() if d)
    # old-period version: same definitions, seed-period data (verified XBRL, else numbers located in the seed context)
    old_results = {}
    for mk, expr in seed_metrics.items():
        v, miss = evaluate(expr, V_verified)
        old_results[mk] = {'formula': expr, 'value': v, 'missing': miss}
    ans_old = make_answer(q5_old, old_results)
    gt_old = gt_text(q5_old, ans_old, old_results, V_verified)
    traj['step5_question'] = {'old_question': question_old, 'old_ground_truth': gt_old, 'old_answer': ans_old,
                              'question': question, 'ground_truth_answer': gt, 'answer': ans, 'accepted_variants': variants_ans,
                              'grading': 'score each listed item; numbers correct if within 1 unit of the last stated decimal place; labels by meaning',
                              'changes_vs_seed': q5.get('changes_vs_seed', [])}

    # ---- step 6
    checks = []
    for k, v in txb.items():
        if not v:
            continue
        item = spec['items'][k.split('@')[0]]
        s = f"{abs(v['value']):.2f}" if item.get('scale') == 'unit' else f"{abs(v['value']):,.0f}"
        if v['concept'] == 'TEXT':   # value was read from the text itself: single source, nothing independent to compare
            checks.append({'key': k, 'value_as_text': s, 'match_mode': 'text_source (single source)', 'found_in_filing_text': True})
            continue
        text = ftext(cik, v['accn'])
        numpat = r'(?<![\d,.])' + re.escape(s) + r'(?![\d])'
        if len(re.sub(r'\D', '', s)) >= 4 or not item.get('text_label'):
            found, mode = bool(re.search(numpat, text)), 'anywhere (>=4 digits)'   # coincidental match unlikely
        else:   # small numbers must appear within ~400 chars after their row label
            found, mode = bool(re.search('(?i)' + item['text_label'] + r'.{0,400}?' + numpat, text)), 'near_label'
        checks.append({'key': k, 'value_as_text': s, 'match_mode': mode, 'found_in_filing_text': found})
    def leaks(q, a):
        return [k for k, v in a.items() if isinstance(v, (int, float)) and re.search(r'(?<![\d,.])' + re.escape(f'{v:,}') + r'(?![\d])', q)]
    leak = leaks(question, ans) + leaks(question_old, ans_old)
    # old and new versions may differ ONLY in their time expressions
    TIME_RX = r'(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}|(?:19|20)\d{2}'
    only_time_changed = re.sub(TIME_RX, '<T>', question) == re.sub(TIME_RX, '<T>', question_old)
    # every scored item must be asked for in the question, and the company must be named
    asked = q5.get('asked', {})
    not_asked = sorted({k.split('@')[0] for k in ans if k.split('@')[0] not in asked or asked[k.split('@')[0]].lower() not in question.lower()})
    company_named = spec.get('company_in_question', '\x00').lower() in question.lower()
    near_boundary = []
    for k, d in q5['answer_decimals'].items():
        x = abs(results[k]['value']) * 10 ** d
        if abs((x - int(x)) - 0.5) < 0.05:
            near_boundary.append({'key': k, 'unrounded': results[k]['value']})
    # the question must not give away the calculation (user rule: test the model's own reasoning)
    formula_hits = re.findall(r'=|\s/\s|\bdivided by\b|\bx 365\b|\bminus\b|\bplus\b|\bdefined as\b|\bdenominator\b|\bsum of\b', question, re.I)
    old_vals_ok = all(old_results[k]['value'] is not None for k in q5_old['answer_decimals'])
    all_vals_ok = all(r['value'] is not None for r in results.values()) and \
                  all(r['value'] is not None for vr in vresults.values() for r in vr.values())
    auto_pass = all(c['found_in_filing_text'] for c in checks) and not leak and not formula_hits and all_vals_ok and \
                only_time_changed and old_vals_ok and not not_asked and company_named
    review = dict(spec.get('step6_review') or {})
    if review.get('verdict', 'auto') in ('auto', 'pending'):   # exception-based review: judge only flagged items
        clean = auto_pass and not traj['step2_backtest']['flags_for_attention']
        review = {**review, 'verdict': 'pass' if clean else 'needs_attention', 'mode': 'auto (no flags)' if clean else 'flagged'}
    traj['step6_review'] = {'text_verification': checks, 'answer_leak_in_question': leak, 'formula_in_question': formula_hits,
                            'only_time_changed_old_vs_new': only_time_changed, 'scored_items_not_asked': not_asked,
                            'company_named_in_question': company_named, 'old_version_values_ok': old_vals_ok,
                            'rounding_near_boundary': near_boundary,
                            'automatic_checks_pass': auto_pass, **review}
    traj['revisions'] = spec.get('revisions', [])
    traj['final_status'] = ('ACCEPTED' if auto_pass and review['verdict'] == 'pass' else
                            'NEEDS_ATTENTION' if review['verdict'] == 'needs_attention' else 'NEEDS_REVISION')

    row = {'new_qid': f'{qid}_u1', 'seed_qid': qid, 'company': spec['company'], 'form': target_meta['form'],
           'accession_number': spec['target_accn'], 'report_period': target_meta['period'], 'filed': target_meta['filed'],
           'seed_original_question': traj['seed']['question'],
           'old_question': question_old, 'old_ground_truth': gt_old, 'old_answer_json': json.dumps(ans_old, ensure_ascii=False),
           'question': question, 'ground_truth_answer': gt, 'answer_json': json.dumps(ans, ensure_ascii=False),
           'accepted_variants_json': json.dumps({k: v for k, v in variants_ans.items() if v}, ensure_ascii=False),
           'status': traj['final_status']}
    return traj, row


def main():
    seed_rows = {r['QID']: r for r in csv.DictReader(open(os.path.join(REPO, 'SecQue_ratio.csv'), encoding='utf-8-sig', newline=''))}
    qids = sys.argv[1:] or sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(STEP0, 'specs', '*.json')))
    os.makedirs(os.path.join(STEP0, 'runs'), exist_ok=True)
    rows = []
    for q in qids:
        traj, row = run(q, seed_rows)
        json.dump(traj, open(os.path.join(STEP0, 'runs', f'{q}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f'{q}: {traj["final_status"]}')
        if row:
            rows.append(row)
    if len(sys.argv) == 1:
        with open(os.path.join(STEP0, 'new_benchmark_agent.csv'), 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['new_qid'])
            w.writeheader(); w.writerows(rows)


if __name__ == '__main__':
    main()
