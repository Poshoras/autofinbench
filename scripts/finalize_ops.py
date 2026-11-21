"""Apply review decisions and per-operator acceptance rules to step1/items.jsonl.
Writes step1/items_final.jsonl and step1/new_items.csv. Usage: python3 -I scripts/finalize_ops.py"""
import json, os, re, csv, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
S1 = os.path.join(ROOT, 'step1')

# seeds whose own SecQue excerpts lack an input of the metric: excerpt-based checking items are not answerable
SEED_CONTEXT_INCOMPLETE = {'q_Ra001': 'seed excerpts contain no income statement, so operating income (EBIT input) cannot be checked from them'}

def num(s):
    m = re.search(r'-?[\d,]+\.?\d*', s); return float(m.group(0).replace(',', '')) if m else None

def main():
    items = [json.loads(l) for l in open(os.path.join(S1, 'items.jsonl'))]
    rev = json.load(open(os.path.join(S1, 'missing_review.json')))
    tv = json.load(open(os.path.join(S1, 'text_verify.json')))
    tv_bad = collections.defaultdict(list)
    for o in tv:
        if not o['found_in_text']: tv_bad[o['qid']].append(f"{o['period']} {o['item']}")
    ctrl = {i['seed_qid']: i['answer']['correct_value'] for i in items if i.get('variant') == 'control'}
    for i in items:
        q, reasons, status = i['seed_qid'], [], 'ACCEPTED'
        c = i.get('checks', {})
        if i.get('skipped'):
            status = 'REJECTED'; reasons.append(i['skipped'])
        elif i['op'] == 'trend':
            if c['tie_for_highest']: status = 'NEEDS_ATTENTION'; reasons.append('tie for highest after rounding')
            if not c['conclusion_stable_under_restatement']: status = 'NEEDS_ATTENTION'; reasons.append('conclusion changes if restated figures are used')
            if c['rounding_boundary']:
                # does a one-unit rounding shift at a boundary period change 'highest' or 'rose every period'?
                d = int(re.search(r'\.(\d+)', i['answer']['values'][0]).group(1).__len__()) if '.' in i['answer']['values'][0] else 0
                ends = [r['end'] for r in i['periods']]
                base = [round(r['first'], d) for r in i['periods']]
                def concl(v):
                    top = max(v); return ([e for e, x in zip(ends, v) if x == top], all(v[k + 1] > v[k] for k in range(len(v) - 1)))
                flips = []
                for e in c['rounding_boundary']:
                    k = ends.index(e) if e in ends else None
                    if k is None: continue
                    for sgn in (1, -1):
                        v = list(base); v[k] = round(v[k] + sgn * 10 ** -d, d)
                        if concl(v) != concl(base): flips.append(e)
                if flips: status = 'NEEDS_ATTENTION'; reasons.append(f'rounding at {sorted(set(flips))} could change the conclusion')
                else: reasons.append(f"near rounding boundary at {c['rounding_boundary']}; a one-unit shift does not change highest/direction")
            notes = {'q_Ra007': 'confirmed by label search: "Interest expense (income), net 33/28/19/54" in each 10-K',
                     'q_an049': 'FY2018 financial statements are in Exhibit 13 (annual report), not the 10-K primary document; not text-checked'}
            if tv_bad.get(q): reasons.append(f"number search missed {tv_bad[q]}: {notes.get(q, 'unresolved')}")
            vals = [num(v) for v in i['answer']['values']]
            if i['metric'].endswith('margin') and any(abs(v) > 100 for v in vals):
                status = 'REJECTED'; reasons.append('implausible margin > 100%')
        elif i['op'] == 'missing':
            if q in rev['unanswerable']:
                reasons.append('non-derivability reviewed: ' + rev['unanswerable'][q])
            elif q in rev['derivable']:
                # the figure can be rebuilt from an accounting identity: the item becomes a 'reconstruct' question
                i['op'] = 'reconstruct'
                i['answer'] = dict(answerable=True, correct_value=ctrl[q], derivation=rev['derivable'][q],
                                   expected='Rebuild the missing figure from the identity, then compute the metric.')
                reasons.append('removed figure is derivable; converted to reconstruct item (GT = original value)')
            elif q in rev.get('unanswerable_other_reason', {}):
                o = rev['unanswerable_other_reason'][q]
                i['answer']['missing_item'] = o['missing_item']
                reasons.append('unanswerable, but not because of the blanked cell: ' + o['note'])
            elif q in rev['answer_printed_in_excerpts']:
                status = 'REJECTED'; reasons.append('answer printed in excerpts: ' + rev['answer_printed_in_excerpts'][q])
            if not c.get('removed_value_absent', True):
                status = 'REJECTED'; reasons.append('removed value still present')
        elif i['op'] == 'verify':
            if q in SEED_CONTEXT_INCOMPLETE:
                status = 'REJECTED'; reasons.append(SEED_CONTEXT_INCOMPLETE[q])
            if 'INVALID' in i.get('error_type', ''):
                status = 'REJECTED'; reasons.append('injected error invisible after rounding')
            if c.get('rounding_boundary'): reasons.append('true value near rounding boundary')
            if i.get('variant') == 'injected_error':
                cv, tv_ = num(i['claim_value']), num(i['answer']['correct_value'])
                rel = abs(cv - tv_) / max(abs(tv_), 1e-9)
                i['checks']['relative_error'] = round(rel, 3)
                if rel > 1: reasons.append('error is gross (>100%); likely easy to spot')
        elif i['op'] == 'cross':
            if c['tie_after_rounding']: status = 'NEEDS_ATTENTION'; reasons.append('tie after rounding')
            if c['concept_differs_between_companies']:
                reasons.append(f"XBRL concept differs between companies: {c['concept_differs_between_companies']} (reviewed: both are the company's total revenue line)")
            if c['period_end_gap_days'] > 7: reasons.append(f"fiscal period ends differ by {c['period_end_gap_days']} days (stated in stem)")
            if c['restated']: reasons.append('an input was later restated; stem pins the original filing')
        i['status'], i['status_reasons'] = status, reasons
    with open(os.path.join(S1, 'items_final.jsonl'), 'w') as f:
        for i in items: f.write(json.dumps(i, ensure_ascii=False) + '\n')
    cols = ['item_id', 'op', 'status', 'seed_qid', 'company', 'metric', 'seed_question', 'question', 'answer', 'status_reasons']
    with open(os.path.join(S1, 'new_items.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(cols)
        for i in items:
            w.writerow([i['item_id'], i['op'], i['status'], i['seed_qid'], i['company'], i['metric'], i['seed_question'],
                        i.get('question', ''), json.dumps(i.get('answer', {}), ensure_ascii=False), ' | '.join(i['status_reasons'])])
    cnt = collections.Counter((i['op'], i['status']) for i in items)
    for k in sorted(cnt): print(k, cnt[k])
    print('companies:', len({i['company'] for i in items} | {list(i['answer']['values'])[1] for i in items if i['op'] == 'cross' and 'values' in i.get('answer', {})}))

if __name__ == '__main__':
    main()
