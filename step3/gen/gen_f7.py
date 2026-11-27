"""F7 candidate: de-cumulate YTD cash-flow facts into discrete quarters (10-Q cash flows are year-to-date)."""
import csv, os, json
from lib import *
from qlib import write_facts, save_gt, q, FACTS_NOTE, REPO
C = 'NetCashProvidedByUsedInOperatingActivities'; X = 'PaymentsToAcquirePropertyPlantAndEquipment'

def ytd(t, c, year):
    out = {}
    for r in sorted(series(t, c), key=lambda r: r['filed']):
        if r.get('start', '')[:4] == str(year) and r['start'][5:] == '01-01' and r['end'][:4] == str(year) and r['form'] in ('10-Q', '10-K') and r['fy'] == year:
            out.setdefault(r['end'], r['val'] / 1e6)   # value as first filed for that YTD period
    return dict(sorted(out.items()))

def quarters(t, year):
    o, x = ytd(t, C, year), ytd(t, X, year)
    ends = list(o); res = {}
    prev_o = prev_x = 0
    for i, e in enumerate(ends):
        res[f'Q{i+1}'] = round((o[e] - prev_o) - (x[e] - prev_x), 1); prev_o, prev_x = o[e], x[e]
    naive = {f'Q{i+1}': round(o[e] - x[e], 1) for i, e in enumerate(ends)}
    return ends, res, naive

def make(qid, t, name, year):
    ends, res, naive = quarters(t, year)
    write_facts(qid, t, [C, X], lambda r: r.get('form') in ('10-Q', '10-K') and f'{year-1}-01-01' <= r['end'] <= f'{year+1}-09-30')
    q(qid, f'{name} quarterly free cash flow, FY{year}', 'F7 multi-period de-cumulation', f"""For {name} ({t}), fiscal year {year}, compute free cash flow (operating cash flow − capital expenditures, tags `{C}` and `{X}`) for each of the four fiscal quarters, in USD millions, using the values **as first reported** for each period. Then give the full-year FCF and the quarter with the lowest FCF.

{FACTS_NOTE}""", '{"Q1": 0.0, "Q2": 0.0, "Q3": 0.0, "Q4": 0.0, "full_year": 0.0, "lowest_quarter": "Q?"}')
    fy = round(sum(res.values()), 1); low = min(res, key=res.get)
    save_gt(qid, {'family': 'F7', 'fields': {**res, 'full_year': fy}, 'lowest_quarter': low, 'tol': {k: 1.0 for k in ['Q1', 'Q2', 'Q3', 'Q4', 'full_year']},
                  'signatures': {'used_ytd_as_quarterly': naive}, 'quarter_ends': ends})
    return res, naive, low

if __name__ == '__main__':
    print(quarters('KO', 2025)); print(quarters('TSLA', 2025))
