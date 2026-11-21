"""Period-aware value lookup on SEC companyfacts, with restatement tracking.

value(cik, concept, end, months) -> dict(first=..., latest=..., values={val: [accn,...]}, ...)
months=0 means an instant (balance-sheet) fact; otherwise a duration of ~months ending on `end`.
"""
import datetime as dt
from edgar import companyfacts

D = dt.date.fromisoformat
WIN = {0: None, 3: (84, 98), 6: (175, 190), 9: (266, 280), 12: (350, 380)}

def _facts(cik, concept, unit=None):
    f = companyfacts(cik)['facts']
    for tax in ('us-gaap', 'dei', 'ifrs-full'):
        c = f.get(tax, {}).get(concept)
        if c:
            units = c['units']
            u = unit or ('USD' if 'USD' in units else next(iter(units)))
            return units.get(u, [])
    return []

def value(cik, concept, end, months, unit=None, tol_days=7):
    end = D(end)
    hits = []
    for x in _facts(cik, concept, unit):
        if x.get('form') not in ('10-K', '10-Q', '10-K/A', '10-Q/A'):
            continue
        e = D(x['end'])
        if abs((e - end).days) > tol_days:
            continue
        if months == 0:
            if 'start' in x: continue
        else:
            if 'start' not in x: continue
            n = (e - D(x['start'])).days
            lo, hi = WIN[months]
            if not (lo <= n <= hi): continue
        hits.append(x)
    if not hits:
        return None
    hits.sort(key=lambda x: x['filed'])
    vals = {}
    for x in hits:
        vals.setdefault(x['val'], []).append(x['accn'])
    return dict(concept=concept, end=hits[0]['end'], first=hits[0]['val'], first_accn=hits[0]['accn'],
                latest=hits[-1]['val'], latest_accn=hits[-1]['accn'], n_filings=len({x['accn'] for x in hits}),
                restated=len(vals) > 1, values={str(k): v for k, v in vals.items()})

def anniversaries(end, n):
    """end date and the same calendar point in the n-1 previous years."""
    e = D(end)
    out = []
    for k in range(n):
        try: out.append(e.replace(year=e.year - k))
        except ValueError: out.append(e.replace(year=e.year - k, day=28))
    return [d.isoformat() for d in reversed(out)]
