"""pass@1 / pass^k over runs k1 (repo answers) + k2,k3 (step3_runs/*.kN.last.md). Full pass = score == 1.0."""
import json, re, os, glob, score
RUNS = os.path.expanduser('~/didigou/autofinbench/step3_runs')
def parse_file(p):
    if not os.path.exists(p) or os.path.getsize(p) == 0: return None, None
    t = open(p).read(); b = re.findall(r'```json\s*(.*?)```', t, re.S)
    if not b: return 'NOJSON', None
    try: return json.loads(b[-1]), '1'
    except Exception: return 'BADJSON', None
orig = score.parse
qids = sorted(os.path.basename(f)[:-5] for f in glob.glob(f'{score.PRIV}/gt/q*.json'))
table = []
for q in qids:
    rs = []
    for k in (1, 2, 3):
        if k == 1: score.parse = orig
        else: score.parse = lambda qid, k=k: parse_file(f'{RUNS}/{qid}.r1.k{k}.last.md')
        r = score.score(q); rs.append(r.get('score', 0.0) if 'score' in r else None)
    fam = json.load(open(f'{score.PRIV}/gt/{q}.json'))['family']
    table.append({'qid': q, 'family': fam, 'scores': rs, 'pass@1': rs[0] == 1.0, 'pass^3': all(s == 1.0 for s in rs if s is not None) and None not in rs})
score.parse = orig
json.dump(table, open(f'{score.PRIV}/reliability.json', 'w'), indent=1)
for t in table: print(t['qid'], t['family'], t['scores'], 'pass^3' if t['pass^3'] else '')
n = len(table); print('pass@1', sum(t['pass@1'] for t in table), '/', n, ' pass^3', sum(bool(t['pass^3']) for t in table), '/', n)
