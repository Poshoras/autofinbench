"""Per-model scores on q001-q025 and AutoBencher-style item statistics over the model set M.
difficulty_i = 1 - max_m score_im ; separability_i = mean_m |score_im - mean_m score_im| (AutoBencher §3.1, item level)."""
import json, re, os, glob, score
RUNS = os.path.expanduser('~/didigou/autofinbench/step3_runs')
MODELS = {'gpt-6-astra': None, 'gpt-6-luna': '.m-gpt-6-luna', 'gpt-5.6-luna': '.m-gpt-5.6-luna'}
def parse_file(p):
    if not os.path.exists(p) or os.path.getsize(p) == 0: return None, None
    t = open(p).read(); b = re.findall(r'```json\s*(.*?)```', t, re.S)
    if not b: return 'NOJSON', None
    try: return json.loads(b[-1]), '1'
    except Exception: return 'BADJSON', None
orig = score.parse
qids = [f'q{i:03d}' for i in range(1, 26)]
tab = {}; sigs = {}
for m, tag in MODELS.items():
    score.parse = orig if tag is None else (lambda qid, tag=tag: parse_file(f'{RUNS}/{qid}.r1{tag}.last.md'))
    for q in qids:
        r = score.score(q); tab[(q, m)] = r.get('score', 0.0) if 'score' in r else 0.0; tab[(q, m, 'L')] = r.get('lenient_score', tab[(q, m)])
        if r.get('signatures'): sigs[(q, m)] = r['signatures']
        if 'score' not in r: sigs[(q, m)] = [r.get('status')]
score.parse = orig
rows = []
for q in qids:
    s = [tab[(q, m)] for m in MODELS]; mu = sum(s) / len(s)
    rows.append({'qid': q, 'family': json.load(open(f'{score.PRIV}/gt/{q}.json'))['family'], **{m: round(tab[(q, m)], 3) for m in MODELS},
                 'lenient': {mm: tab[(q, mm, 'L')] for mm in MODELS}, 'difficulty': round(1 - max(s), 3), 'separability': round(sum(abs(x - mu) for x in s) / len(s), 3),
                 'signatures': {m: sigs.get((q, m)) for m in MODELS if sigs.get((q, m))}})
json.dump(rows, open(f'{score.PRIV}/model_matrix.json', 'w'), indent=1)
for r in rows: print(r['qid'], r['family'], [r[m] for m in MODELS], 'sep', r['separability'], r['signatures'] or '')
for m in MODELS:
    v = [tab[(q, m)] for q in qids]; L = [tab[(q, m, 'L')] for q in qids]
    print(m, 'strict mean', round(sum(v) / len(v), 3), 'full-pass', sum(x == 1.0 for x in v), '/', len(v), '| lenient full-pass', sum(x == 1.0 for x in L))
