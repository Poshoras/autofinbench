"""Round 4: haystack (all HON us-gaap facts 2024+, ~4k rows) with as-of + YTD + recast traps; GT computed from the env file."""
import csv, os, json
from lib import *
from qlib import write_facts, save_gt, q, FACTS_NOTE, REPO

concepts = list(facts('HON')['facts']['us-gaap'].keys())
n = write_facts('q024', 'HON', concepts, lambda r: r['end'] >= '2024-01-01' and r.get('form') in ('10-K', '10-Q'))
rows = list(csv.DictReader(open(f'{REPO}/env/q024/facts.csv')))
def first(c, s, e, asof='9999'):
    rs = sorted([r for r in rows if r['concept'] == c and r['start'] == s and r['end'] == e and r['filed'] <= asof], key=lambda r: r['filed'])
    return float(rs[0]['val']) / 1e6 if rs else None
def latest(c, s, e, asof='9999'):
    rs = sorted([r for r in rows if r['concept'] == c and r['start'] == s and r['end'] == e and r['filed'] <= asof], key=lambda r: r['filed'])
    return float(rs[-1]['val']) / 1e6 if rs else None
T = 'IncomeTaxExpenseBenefit'; P = 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest'
A = '2025-11-30'
etr = latest(T, '2025-01-01', '2025-09-30', A) / latest(P, '2025-01-01', '2025-09-30', A) * 100
rd_q3 = latest('ResearchAndDevelopmentExpense', '2025-01-01', '2025-09-30', A) - latest('ResearchAndDevelopmentExpense', '2025-01-01', '2025-06-30', A)
cash = latest('CashAndCashEquivalentsAtCarryingValue', '', '2025-09-30', A)
bb_q3 = latest('PaymentsForRepurchaseOfCommonStock', '2025-01-01', '2025-09-30', A) - latest('PaymentsForRepurchaseOfCommonStock', '2025-01-01', '2025-06-30', A)
pre_now = latest(P, '2025-01-01', '2025-09-30', '2026-11-15'); pre_orig = first(P, '2025-01-01', '2025-09-30')
gt = {'etr_9m2025_pct': etr, 'rd_q3_2025_usd_m': rd_q3, 'cash_2025_09_30_usd_m': cash, 'buyback_q3_2025_usd_m': bb_q3, 'pretax_9m2025_as_presented_now_usd_m': pre_now, 'pretax_9m2025_as_originally_reported_usd_m': pre_orig}
sig = {'PIT_violation_recast_ETR': {'etr_9m2025_pct': latest(T, '2025-01-01', '2025-09-30') / latest(P, '2025-01-01', '2025-09-30') * 100},
       'ytd_as_quarter': {'rd_q3_2025_usd_m': latest('ResearchAndDevelopmentExpense', '2025-01-01', '2025-09-30', A), 'buyback_q3_2025_usd_m': latest('PaymentsForRepurchaseOfCommonStock', '2025-01-01', '2025-09-30', A)}}
q('q024', 'Honeywell data pack from the full fact export', 'F11 haystack: as-of + YTD + recast at scale', f"""`facts.csv` is the **full** US-GAAP fact export for Honeywell (HON) for periods ending 2024-01-01 or later ({n} rows, all 10-K/10-Q filings through 2026-10).

Part A — for a note dated **2025-11-30** (use only what was public on that date):
1. Effective tax rate for the nine months ended 2025-09-30 (`IncomeTaxExpenseBenefit` / `{P}`), percent.
2. R&D expense for the three months ended 2025-09-30, USD millions.
3. Cash and cash equivalents at 2025-09-30, USD millions.
4. Share repurchases (cash paid) in the three months ended 2025-09-30, USD millions.

Part B — today (2026-11-15):
5. Pre-tax income from continuing operations for the nine months ended 2025-09-30 as currently presented, and as originally reported, USD millions.

{FACTS_NOTE}""", '{"etr_9m2025_pct": 0.0, "rd_q3_2025_usd_m": 0.0, "cash_2025_09_30_usd_m": 0.0, "buyback_q3_2025_usd_m": 0.0, "pretax_9m2025_as_presented_now_usd_m": 0.0, "pretax_9m2025_as_originally_reported_usd_m": 0.0}')
save_gt('q024', {'family': 'F11', 'fields': gt, 'tol': {'etr_9m2025_pct': 0.02, **{k: 1.0 for k in gt if k != 'etr_9m2025_pct'}}, 'signatures': sig})
print(n, json.dumps(gt), os.path.getsize(f'{REPO}/env/q024/facts.csv'))
