"""Build the DeepSeek evaluation set: step1/eval/prompts.jsonl (what the model sees) and
step1/eval/gold.jsonl (what the scorer uses). Usage: python3 -I scripts/build_eval.py"""
import json, os, re, glob
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
S1 = os.path.join(ROOT, 'step1'); OUT = os.path.join(S1, 'eval')
SECQUE = os.path.join(ROOT, '..', 'data', 'secque_full')

SYSTEM = (
    "You are a financial analyst answering questions about SEC filings.\n"
    "Rules:\n"
    "1. Use only the filing excerpts in the user message. Do not use figures from memory or any outside source.\n"
    "2. A figure that is not printed may be derived from other figures in the excerpts when an accounting identity "
    "makes it exact (for example, a total minus its other components).\n"
    "3. If the excerpts still do not contain what is needed, say that the question cannot be answered and name the "
    "missing item. Do not estimate.\n"
    "4. Show brief working, then end your reply with exactly one JSON object in the requested format and nothing after it.")

UNIT = {'p': ('percent', 'a number in percent, e.g. 12.3 for 12.3%'),
        'x': ('times', 'a number of times, e.g. 2.15 for 2.15x'),
        'm': ('USD millions', 'a number in millions of US dollars, e.g. 4379 for $4,379 million')}

def num(s):
    m = re.search(r'-?[\d,]*\.?\d+', str(s)); return float(m.group(0).replace(',', '')) if m else None

def fmt_block(op, unit_desc, extra=None):
    if op == 'compute':
        return ('{"answerable": true or false, "value": <' + unit_desc + ', or null if not answerable>, '
                '"missing_item": "<the missing item, or null>"}')
    if op == 'trend':
        return ('{"values": [<five numbers, each ' + unit_desc + ', in the order the periods are listed>], '
                '"highest_period_end": "<YYYY-MM-DD>", "increased_every_period": true or false}')
    if op == 'verify':
        return ('{"statement_correct": true or false, "error": "<what is wrong, or null>", '
                '"correct_value": <' + unit_desc + '>}')
    if op == 'cross':
        a, b = extra
        vdesc, ddesc = unit_desc
        return ('{"values": {"' + a + '": <' + vdesc + '>, "' + b + '": <' + vdesc + '>}, "higher": "<' + a + ' or ' + b + '>", '
                '"difference": <a number in ' + ddesc + '>}')

def user_msg(context, question, block):
    return (f"FILING EXCERPTS\n{context}\n\nQUESTION\n{question}\n\n"
            f"ANSWER FORMAT\nEnd your reply with one JSON object of this form:\n{block}")

def main():
    seeds = {s['qid']: s for s in json.load(open(os.path.join(S1, 'seeds.json')))}
    secq = {}
    for f in glob.glob(os.path.join(SECQUE, '*.jsonl')):
        for l in open(f):
            d = json.loads(l); secq[d['QID']] = d
    items = [json.loads(l) for l in open(os.path.join(S1, 'items_final.jsonl'))]
    ctxs = json.load(open(os.path.join(OUT, 'contexts.json')))
    by = {(i['seed_qid'], i['op'], i.get('variant')): i for i in items}
    prompts, gold = [], []

    def add(item_id, op, variant, it, context, question, opfmt, g, main_score=True, note=''):
        s = seeds[it['seed_qid']]
        unit, desc = UNIT[s['fmt'][0]]
        if opfmt == 'cross':
            names = list(it['answer']['values'])
            dunit = 'percentage points' if s['fmt'][0] == 'p' else unit
            block = fmt_block('cross', (desc, dunit), names)
        else:
            block = fmt_block(opfmt, desc)
        prompts.append(dict(item_id=item_id, op=op, variant=variant, seed_qid=it['seed_qid'], company=it['company'],
                            system=SYSTEM, user=user_msg(context, question, block)))
        d = int(s['fmt'][1:])
        gold.append(dict(item_id=item_id, op=op, variant=variant, seed_qid=it['seed_qid'], company=it['company'],
                         metric=it['metric'], unit=unit, display_decimals=d, in_main_score=main_score, note=note, **g))

    for q, s in seeds.items():
        seed_ctx = secq[q]['context_markdown_with_headers']
        miss = by.get((q, 'missing', None)) or by.get((q, 'reconstruct', None))
        ctrl = by.get((q, 'verify', 'control'))
        # base: the seed-period computation on the unmodified seed excerpts (same question text as the missing item)
        if miss and ctrl and ctrl['status'] == 'ACCEPTED':
            add(f'{q}_base', 'base', None, miss, seed_ctx, miss['question'], 'compute',
                dict(answerable=True, value=num(ctrl['answer']['correct_value']), value_display=ctrl['answer']['correct_value']))
        for it in [i for i in items if i['seed_qid'] == q and i['status'] != 'REJECTED']:
            main = it['status'] == 'ACCEPTED'
            if it['op'] == 'missing':
                add(it['item_id'], 'missing', None, it, it['context_modified'], it['question'], 'compute',
                    dict(answerable=False, missing_item=it['answer']['missing_item']), main)
            elif it['op'] == 'reconstruct':
                g = dict(answerable=True, value=num(it['answer']['correct_value']), value_display=it['answer']['correct_value'],
                         derivation=it['answer']['derivation'])
                if q == 'q_com146': g['accept_range'] = [13.5, 13.7]
                add(it['item_id'], 'reconstruct', None, it, it['context_modified'], it['question'], 'compute', g, main)
            elif it['op'] == 'verify':
                g = dict(statement_correct=it['answer']['correct'], correct_value=num(it['answer']['correct_value']),
                         correct_value_display=it['answer']['correct_value'], claim_value=num(it['claim_value']))
                if not it['answer']['correct']: g.update(error=it['answer']['error'], error_type=it['error_type'])
                add(it['item_id'], 'verify', it['variant'], it, seed_ctx, it['question'], 'verify', g, main)
            elif it['op'] == 'trend':
                a, b = it['answer'], it['answer_if_latest_restated']
                g = dict(values=[num(v) for v in a['values']], values_display=a['values'], highest_period_end=a['highest'],
                         increased_every_period=a['rose_every_period'], period_ends=[p['end'] for p in it['periods']],
                         if_latest_restated=dict(values=[num(v) for v in b['values']], highest_period_end=b['highest'],
                                                 increased_every_period=b['rose_every_period']))
                add(it['item_id'], 'trend', None, it, ctxs[it['item_id']]['context'], it['question'], 'trend', g, main,
                    note='; '.join(it['status_reasons']) if not main else '')
            elif it['op'] == 'cross':
                a = it['answer']
                g = dict(values={k: num(v) for k, v in a['values'].items()}, values_display=a['values'], higher=a['higher'],
                         difference=num(a['difference']))
                add(it['item_id'], 'cross', None, it, ctxs[it['item_id']]['context'], it['question'], 'cross', g, main)
    with open(os.path.join(OUT, 'prompts.jsonl'), 'w') as f:
        for p in prompts: f.write(json.dumps(p, ensure_ascii=False) + '\n')
    with open(os.path.join(OUT, 'gold.jsonl'), 'w') as f:
        for g in gold: f.write(json.dumps(g, ensure_ascii=False) + '\n')
    import collections
    c = collections.Counter((g['op'], g['in_main_score']) for g in gold)
    for k in sorted(c): print(k, c[k])
    print('prompts', len(prompts), 'max user chars', max(len(p['user']) for p in prompts))

if __name__ == '__main__':
    main()
