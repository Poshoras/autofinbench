"""Round 5: F12 PIT audit of someone else's claims (inline-able); F13 tool-tier cross-company scans (spec + GT only)."""
import csv, os, json, random, datetime as dt
from lib import *
from qlib import write_facts, save_gt, q, FACTS_NOTE, REPO
R1, R2 = 'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax'
SPEC = {'HON': [R2, 'PaymentsToAcquirePropertyPlantAndEquipment'], 'PFE': [R1], 'NVDA': ['EarningsPerShareDiluted'], 'TSLA': [R1, 'PaymentsToAcquirePropertyPlantAndEquipment'], 'KO': [R2], 'AXP': ['RevenuesNetOfInterestExpense']}
d = f'{REPO}/env/q025'; os.makedirs(d, exist_ok=True)
allrows = []
for t, cs in SPEC.items():
    for c in cs:
        for r in annual(series(t, c)):
            if '2022-01-01' <= r['end'] <= '2025-12-31':
                allrows.append({'ticker': t, 'concept': c, 'start': r['start'], 'end': r['end'], 'val': r['val'], 'form': r['form'], 'filed': r['filed'], 'accn': r['accn']})
allrows.sort(key=lambda r: (r['ticker'], r['concept'], r['end'], r['filed']))
with open(f'{d}/facts.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(allrows[0])); w.writeheader(); w.writerows(allrows)
def versions(t, c, end):
    return sorted([r for r in allrows if r['ticker'] == t and r['concept'] == c and r['end'] == end], key=lambda r: r['filed'])
def pit_value(t, c, end, asof):
    v = [r for r in versions(t, c, end) if r['filed'] <= asof]; return v[-1]['val'] if v else None
rnd = random.Random(25); claims = []; gt = {}
keys = sorted({(r['ticker'], r['concept'], r['end']) for r in allrows})
def fmt(t, c, v): return v if c == 'EarningsPerShareDiluted' else v / 1e6
cid = 0
for (t, c, end) in keys:
    vs = versions(t, c, end); first_filed = vs[0]['filed']
    later = [r for r in vs if r['val'] != vs[0]['val']]
    kinds = ['ok', 'incorrect']
    if later: kinds += ['pit_violation_recast'] * 2
    kinds += ['pit_violation_not_yet_reported']
    kind = rnd.choice(kinds)
    if later and t != 'NVDA': kind = 'pit_violation_recast'   # every genuine recast becomes a look-ahead trap (NVDA split excluded: split-adjusting a known split is defensible)
    if kind == 'ok':
        asof = (dt.date.fromisoformat(first_filed) + dt.timedelta(days=rnd.randint(1, 200))).isoformat(); val = pit_value(t, c, end, asof)
    elif kind == 'incorrect':
        asof = (dt.date.fromisoformat(first_filed) + dt.timedelta(days=rnd.randint(1, 200))).isoformat(); val = pit_value(t, c, end, asof)
        val = round(val * rnd.choice([0.9, 1.1, 1.01]), 2) if c == 'EarningsPerShareDiluted' else round(val * rnd.choice([0.9, 1.1, 0.99]) / 1e6) * 1e6
    elif kind == 'pit_violation_recast':
        asof = (dt.date.fromisoformat(later[0]['filed']) - dt.timedelta(days=rnd.randint(5, 120))).isoformat()
        if asof < first_filed: asof = first_filed
        val = later[0]['val']
    else:
        asof = (dt.date.fromisoformat(first_filed) - dt.timedelta(days=rnd.randint(3, 40))).isoformat(); val = vs[0]['val']
    cid += 1; k = f'C{cid:02d}'
    claims.append({'claim_id': k, 'note_date': asof, 'ticker': t, 'metric_tag': c, 'period_end': end, 'claimed_value': fmt(t, c, val), 'unit': 'USD/share' if c == 'EarningsPerShareDiluted' else 'USD millions'})
    gt[k] = 'pit_violation' if kind.startswith('pit') else kind
with open(f'{d}/claims.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(claims[0])); w.writeheader(); w.writerows(claims)
q('q025', 'Audit an analyst’s figures for look-ahead', 'F12 point-in-time audit (reviewer role)', """`claims.csv` lists figures that appeared in past research notes (note date, company, XBRL tag, fiscal period end, claimed annual value). `facts.csv` is the filing history for those tags (annual values from 10-K filings, with filing dates; the same period can appear in several filings).

Audit every claim. Classify each as:
- `ok` — the claimed value matches what was publicly filed for that period on or before the note date (latest such filing);
- `pit_violation` — the claim uses information that was not yet public on the note date (a value first filed after the note date, or a period not yet reported at all);
- `incorrect` — any other mismatch.

EPS is in USD/share; other values in USD millions.""", '{"C01": "ok", "C02": "pit_violation", "...": "incorrect"}')
save_gt('q025', {'family': 'F12', 'labels': gt})
print('q025 claims', len(claims), {k: list(gt.values()).count(k) for k in set(gt.values())})

# F13 tool tier (spec + GT only; environment = cached SEC companyfacts for the 24 CIKs, facts filed <= 2026-11-15)
import glob
CIKS = sorted(int(os.path.basename(f)[6:-5]) for f in glob.glob(os.path.expanduser('~/didigou/autofinbench/repo/data/edgar/facts_*.json')))
rev_hits = []
for f in glob.glob(os.path.expanduser('~/didigou/autofinbench/repo/data/edgar/facts_*.json')):
    dd = json.load(open(f)); name = dd['entityName']; g = dd['facts'].get('us-gaap', {})
    for c in (R1, R2, 'RevenuesNetOfInterestExpense'):
        for u, xs in g.get(c, {}).get('units', {}).items():
            by = {}
            for x in xs:
                if x.get('form', '').startswith('10-K') and x.get('start') and x['filed'] <= '2026-11-15':
                    if not (350 <= (dt.date.fromisoformat(x['end']) - dt.date.fromisoformat(x['start'])).days <= 380): continue
                    if x['end'][:4] not in ('2023', '2024'): continue
                    by.setdefault(x['end'], []).append(x)
            for end, xs2 in by.items():
                xs2.sort(key=lambda x: x['filed']); v0 = xs2[0]['val']; vmax = max(xs2, key=lambda x: abs(x['val'] - v0))
                if v0 and abs(vmax['val'] - v0) / abs(v0) > 0.05:
                    rev_hits.append({'cik': dd['cik'], 'entity': name, 'tag': c, 'period_end': end, 'first_reported': v0, 'max_revised': vmax['val'], 'pct_change': round((vmax['val'] - v0) / v0 * 100, 2)})
rev_hits.sort(key=lambda h: (h['cik'], h['tag'], h['period_end']))
open(f'{REPO}/questions/q026.md', 'w').write(f"""# q026 · Cross-company revenue revisions (tool tier)

- **Revision:** 1
- **Family:** F13 tool-tier scan (requires code execution; not run in the 2-hour session)
- **Environment:** SEC EDGAR companyfacts JSON (`https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`) for these CIKs: {', '.join(str(c) for c in CIKS)}. **Use only facts with `filed` ≤ 2026-11-15.** (The maintainer's cached copy lives in `data/edgar/`, gitignored and re-fetchable with `scripts/edgar.py`.)

For every company, consider annual (350–380 day) 10-K facts for the tags `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax` and `RevenuesNetOfInterestExpense` for fiscal periods ending in calendar 2023 or 2024. List every (company, tag, period end) whose value was later revised in a subsequent 10-K by more than 5% (absolute) versus the value first reported.

## Answer format
End with one fenced `json` block: a list of objects `{{"cik": 0, "tag": "...", "period_end": "YYYY-MM-DD", "first_reported": 0, "max_revised": 0}}`.
""")
save_gt('q026', {'family': 'F13', 'hits': rev_hits})
print('q026 hits', len(rev_hits))
