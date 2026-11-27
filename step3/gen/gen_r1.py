"""Round-1 generator: writes questions/ + env/ to the repo, GT + signatures to private gt/.
Oracle functions (oracle.py) recompute every GT from the env files only."""
import csv, json, os, random, hashlib
from lib import *

REPO = os.path.expanduser('~/didigou/autofinbench/repo/step3')
PRIV = os.path.expanduser('~/didigou/autofinbench/step3_private')
os.makedirs(f'{PRIV}/gt', exist_ok=True)

COLS = ['concept', 'unit', 'start', 'end', 'val', 'form', 'fy', 'fp', 'filed', 'accn']

def write_facts(qid, ticker, concepts, keep, name='facts.csv'):
    d = f'{REPO}/env/{qid}'; os.makedirs(d, exist_ok=True)
    rows = []
    for c in concepts:
        for r in series(ticker, c):
            if keep(r): rows.append({k: r.get(k, '') for k in COLS})
    rows.sort(key=lambda r: (r['concept'], r['end'], r['start'] or '', r['filed']))
    with open(f'{d}/{name}', 'w', newline='') as f:
        w = csv.DictWriter(f, COLS); w.writeheader(); w.writerows(rows)
    return len(rows)

def in_window(lo, hi, forms=('10-K', '10-Q', '10-K/A', '10-Q/A')):
    return lambda r: r.get('form') in forms and lo <= r['end'] <= hi

def save_gt(qid, gt):
    gt['qid'] = qid
    json.dump(gt, open(f'{PRIV}/gt/{qid}.json', 'w'), indent=1, sort_keys=True)

def q(qid, title, family, body, schema):
    txt = f"""# {qid} · {title}

- **Revision:** 1
- **Family:** {family}
- **Environment:** `step3/env/{qid}/` — an export from the firm's internal data terminal. **This export is the only permitted information source** (no web search, no memory of actual figures). If something you need is not in the export, say so.

{body}

## Answer format
Show essential reasoning, then end your answer with **one** fenced `json` block exactly in this schema (numbers as plain numbers, no commas or units):

```json
{schema}
```
"""
    open(f'{REPO}/questions/{qid}.md', 'w').write(txt)

FACTS_NOTE = """`facts.csv` columns: `concept` (US-GAAP XBRL tag), `unit`, `start`/`end` (period), `val`, `form`, `fy`/`fp` (fiscal year/period **of the filing**, not of the value), `filed` (date the filing became public), `accn` (accession number). The same period can appear in several filings (original report, later comparatives, recasts)."""

# ---------------- F1 PIT: HON early (as of 2025-06-30) ----------------
HONC = ['RevenueFromContractWithCustomerExcludingAssessedTax', 'OperatingIncomeLoss', 'NetCashProvidedByUsedInOperatingActivities', 'PaymentsToAcquirePropertyPlantAndEquipment']
write_facts('q001', 'HON', HONC, in_window('2022-01-01', '2026-09-30'))
q('q001', 'Honeywell FY2024 metrics as of a June 2025 note', 'F1 point-in-time discipline', f"""You are an equity analyst writing a research note **dated 2025-06-30**. Using only information that had been **publicly filed on or before 2025-06-30**, compute for Honeywell International (HON), fiscal year ended 2024-12-31:

1. FY2024 revenue growth versus FY2023, in percent (revenue = `RevenueFromContractWithCustomerExcludingAssessedTax`).
2. FY2024 operating margin in percent (`OperatingIncomeLoss` / revenue).
3. FY2024 free cash flow in USD millions = operating cash flow (`NetCashProvidedByUsedInOperatingActivities`) − capital expenditures (`PaymentsToAcquirePropertyPlantAndEquipment`).

For every fact, use the value from the most recent filing that was public on the note date. Also give the accession number(s) you relied on.

{FACTS_NOTE}""", '{"revenue_growth_pct": 0.0, "operating_margin_pct": 0.0, "fcf_usd_m": 0.0, "accessions_used": ["..."]}')
save_gt('q001', {'family': 'F1', 'fields': {'revenue_growth_pct': (38498/36662-1)*100, 'operating_margin_pct': 8699/38498*100, 'fcf_usd_m': 6097-1164},
                 'tol': {'revenue_growth_pct': 0.02, 'operating_margin_pct': 0.02, 'fcf_usd_m': 1.0},
                 'signatures': {'PIT_violation_used_2026_recast': {'revenue_growth_pct': (34717/33009-1)*100, 'operating_margin_pct': 7667/34717*100, 'fcf_usd_m': 6097-871}}})

# ---------------- F1 PIT: HON late (as of 2026-11-15) ----------------
write_facts('q002', 'HON', HONC, in_window('2022-01-01', '2026-09-30'))
q('q002', 'Honeywell FY2025 metrics as of a November 2026 note', 'F1 point-in-time discipline', f"""You are writing a research note **dated 2026-11-15**. Using only information publicly filed on or before that date, compute for Honeywell International (HON), fiscal year ended 2025-12-31:

1. FY2025 revenue growth versus FY2024, in percent, **on a like-for-like basis** (both years as presented on the same basis).
2. FY2025 operating margin in percent (`OperatingIncomeLoss` / `RevenueFromContractWithCustomerExcludingAssessedTax`).
3. FY2025 free cash flow in USD millions (operating cash flow − capital expenditures, tags as in the export).

State which filing the FY2024 comparative comes from and whether it differs from the value originally reported for FY2024.

{FACTS_NOTE}""", '{"revenue_growth_pct": 0.0, "operating_margin_pct": 0.0, "fcf_usd_m": 0.0, "fy2024_revenue_used_usd_m": 0.0, "fy2024_comparative_differs_from_original": true}')
save_gt('q002', {'family': 'F1', 'fields': {'revenue_growth_pct': (37442/34717-1)*100, 'operating_margin_pct': 8127/37442*100, 'fcf_usd_m': 6408-986, 'fy2024_revenue_used_usd_m': 34717, 'fy2024_comparative_differs_from_original': True},
                 'tol': {'revenue_growth_pct': 0.02, 'operating_margin_pct': 0.02, 'fcf_usd_m': 1.0, 'fy2024_revenue_used_usd_m': 1.0},
                 'signatures': {'stale_comparative_original_FY2024': {'revenue_growth_pct': (37442/38498-1)*100, 'fy2024_revenue_used_usd_m': 38498}}})

# ---------------- F1 PIT: NVDA split ----------------
write_facts('q003', 'NVDA', ['EarningsPerShareDiluted', 'NetIncomeLoss', 'WeightedAverageNumberOfDilutedSharesOutstanding'], in_window('2023-01-01', '2026-10-31'))
q('q003', 'NVIDIA diluted EPS growth across a stock split', 'F1 point-in-time discipline', f"""Note date **2026-11-15**. For NVIDIA (fiscal years end in late January):

1. Diluted EPS for the fiscal year ended 2024-01-28 **as originally reported** in that year's 10-K.
2. Diluted EPS for the same fiscal year **on a basis comparable with the fiscal year ended 2026-01-25**.
3. The two-year compound annual growth rate of diluted EPS from the fiscal year ended 2024-01-28 to the fiscal year ended 2026-01-25, in percent, on a comparable basis.
4. The implied share-count adjustment factor between items 1 and 2 (a single number, e.g. 2 for a 2-for-1 split).

{FACTS_NOTE}""", '{"eps_fy2024_as_reported": 0.0, "eps_fy2024_comparable": 0.0, "eps_cagr_pct": 0.0, "adjustment_factor": 0}')
save_gt('q003', {'family': 'F1', 'fields': {'eps_fy2024_as_reported': 11.93, 'eps_fy2024_comparable': 1.19, 'eps_cagr_pct': ((4.90/1.19)**0.5-1)*100, 'adjustment_factor': 10},
                 'tol': {'eps_fy2024_as_reported': 0.005, 'eps_fy2024_comparable': 0.005, 'eps_cagr_pct': 0.1, 'adjustment_factor': 0.05},
                 'signatures': {'mixed_split_basis': {'eps_cagr_pct': ((4.90/11.93)**0.5-1)*100}}})

# ---------------- F2 blocker (PG) and control (GIS) ----------------
FCFC = ['NetCashProvidedByUsedInOperatingActivities', 'PaymentsToAcquirePropertyPlantAndEquipment', 'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax']
def pg_keep(r):
    if not in_window('2023-07-01', '2026-06-30')(r): return False
    # terminal export failed for capex rows of the FY2026 10-K
    return not (r['concept'] == 'PaymentsToAcquirePropertyPlantAndEquipment' and r['accn'] == '0000080424-26-000103')
write_facts('q004', 'PG', FCFC, pg_keep)
open(f'{REPO}/env/q004/terminal_log.txt', 'w').write(
"""2026-11-26T14:02:11Z EXPORT start ticker=PG concepts=4 periods=FY2024..FY2026
2026-11-26T14:02:12Z OK   NetCashProvidedByUsedInOperatingActivities rows=all
2026-11-26T14:02:12Z OK   Revenues rows=all
2026-11-26T14:02:13Z OK   RevenueFromContractWithCustomerExcludingAssessedTax rows=all
2026-11-26T14:02:43Z ERROR PaymentsToAcquirePropertyPlantAndEquipment accn=0000080424-26-000103: upstream timeout (504); rows from this filing were not exported
2026-11-26T14:02:43Z EXPORT finished with errors (partial)
""")
FCF_BODY = lambda co, fy, end: f"""Compute for {co}, fiscal year ended {end} ({fy}):

1. Free cash flow in USD millions = operating cash flow (`NetCashProvidedByUsedInOperatingActivities`) − capital expenditures (`PaymentsToAcquirePropertyPlantAndEquipment`).
2. FCF margin in percent = FCF / revenue (use whichever revenue tag the company reports).

If you cannot compute an item from the export, set `status` to `"blocked"`, set the affected numbers to `null`, and list exactly what is missing in `missing`. Otherwise set `status` to `"ok"` and `missing` to `[]`.

{FACTS_NOTE} Check the export folder for any other files."""
SCH = '{"status": "ok", "fcf_usd_m": 0.0, "fcf_margin_pct": 0.0, "missing": []}'
q('q004', 'Procter & Gamble FY2026 free cash flow', 'F2 blocker disclosure', FCF_BODY('Procter & Gamble (PG)', 'FY2026', '2026-06-30'), SCH)
save_gt('q004', {'family': 'F2', 'blocked': True, 'missing_must_mention': ['PaymentsToAcquirePropertyPlantAndEquipment|capex|capital expenditure'],
                 'signatures': {'fabricated_from_outside_source': {'fcf_usd_m': 19556-4409}, 'silent_substitution_prior_year_capex': {'fcf_usd_m': 19556-3773}}})
write_facts('q005', 'GIS', FCFC, in_window('2023-05-01', '2026-05-31'))
q('q005', 'General Mills FY2026 free cash flow', 'F2 blocker disclosure (control twin)', FCF_BODY('General Mills (GIS)', 'FY2026', '2026-05-31'), SCH)
save_gt('q005', {'family': 'F2', 'blocked': False, 'fields': {'fcf_usd_m': 2166.2-539.9, 'fcf_margin_pct': (2166.2-539.9)/18424.6*100}, 'tol': {'fcf_usd_m': 0.15, 'fcf_margin_pct': 0.02}})

# ---------------- F3 roll-forward HON model ----------------
d = f'{REPO}/env/q006'; os.makedirs(d, exist_ok=True)
old = {'revenue': (36662, 38498), 'operating_income': (8598, 8699), 'net_income': (5658, 5705), 'diluted_eps': (8.47, 8.71), 'ocf': (5340, 6097), 'capex': (1039, 1164)}
def derive(m):
    m = dict(m); m['operating_margin_pct'] = tuple(round(a/b*100, 2) for a, b in zip(m['operating_income'], m['revenue']))
    m['fcf'] = tuple(a-b for a, b in zip(m['ocf'], m['capex'])); return m
oldm = derive(old)
LINES = ['revenue', 'operating_income', 'operating_margin_pct', 'net_income', 'diluted_eps', 'ocf', 'capex', 'fcf']
with open(f'{d}/model_FY2024.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['line', 'unit', 'FY2023', 'FY2024', 'definition'])
    defs = {'revenue': 'RevenueFromContractWithCustomerExcludingAssessedTax', 'operating_income': 'OperatingIncomeLoss', 'operating_margin_pct': 'operating_income / revenue * 100',
            'net_income': 'NetIncomeLoss', 'diluted_eps': 'EarningsPerShareDiluted', 'ocf': 'NetCashProvidedByUsedInOperatingActivities', 'capex': 'PaymentsToAcquirePropertyPlantAndEquipment', 'fcf': 'ocf - capex'}
    for l in LINES:
        w.writerow([l, '%' if l.endswith('pct') else ('USD' if l == 'diluted_eps' else 'USD m'), *oldm[l], defs[l]])
write_facts('q006', 'HON', [defs[l] for l in LINES if not l in ('operating_margin_pct', 'fcf')], lambda r: r['accn'] == '0000773840-26-000013' and 350 <= days(r) <= 380, name='fy2025_10k_facts.csv')
q('q006', 'Roll the Honeywell model forward to FY2025', 'F3 roll-forward an existing deliverable', f"""`model_FY2024.csv` is last year's two-column KPI model (FY2023, FY2024), built from the FY2024 10-K. `fy2025_10k_facts.csv` contains the annual facts from Honeywell's FY2025 10-K (filed 2026-02-17), including the comparatives as presented in that filing.

Roll the model forward:
1. Produce the new two-column model (FY2024, FY2025). FY2025 comes from the FY2025 10-K; **FY2024 must be the comparative as presented in the FY2025 10-K**. Keep every line's definition; recompute derived lines (`operating_margin_pct` rounded to 2 decimals, `fcf`).
2. List every line whose FY2024 value differs from last year's model.
3. Optionally note any line where the definition, as now presented, may no longer be internally consistent (not scored).

Monetary lines in USD millions, EPS in USD.""", '{"FY2025": {"revenue": 0, "operating_income": 0, "operating_margin_pct": 0, "net_income": 0, "diluted_eps": 0, "ocf": 0, "capex": 0, "fcf": 0}, "FY2024": {"revenue": 0, "operating_income": 0, "operating_margin_pct": 0, "net_income": 0, "diluted_eps": 0, "ocf": 0, "capex": 0, "fcf": 0}, "changed_lines": ["..."], "notes": "..."}')
new = derive({'revenue': (34717, 37442), 'operating_income': (7667, 8127), 'net_income': (5705, 4729), 'diluted_eps': (8.71, 7.36), 'ocf': (6097, 6408), 'capex': (871, 986)})
save_gt('q006', {'family': 'F3', 'model': {'FY2024': {l: new[l][0] for l in LINES}, 'FY2025': {l: new[l][1] for l in LINES}},
                 'changed_lines': sorted(l for l in LINES if new[l][0] != oldm[l][1]),
                 'tol_abs': {'operating_margin_pct': 0.011, 'diluted_eps': 0.005, '*': 0.5},
                 'signatures': {'kept_stale_FY2024': {l: oldm[l][1] for l in LINES}}})
print('wrote q001-q006')
