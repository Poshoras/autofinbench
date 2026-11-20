"""Look up XBRL facts (from companyfacts) by concept / accession / period."""
import sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edgar

def _days(s, e):
    return (dt.date.fromisoformat(e) - dt.date.fromisoformat(s)).days

def facts(cik, concept, accn=None, taxonomy='us-gaap', unit=None):
    f = edgar.companyfacts(cik)['facts'].get(taxonomy, {}).get(concept)
    if not f: return []
    out = []
    for u, rows in f['units'].items():
        if unit and u != unit: continue
        for r in rows:
            if accn and r['accn'] != accn: continue
            out.append(dict(r, unit=u, concept=concept, dur=_days(r['start'], r['end']) if 'start' in r else None))
    return out

def pick(cik, concepts, accn, end, dur=None, unit='USD'):
    """First concept (in priority order) with a fact in filing `accn` for period ending `end`.
    dur: None for instant facts, or approx duration in days (e.g. 365, 91, 182)."""
    for c in concepts:
        for r in facts(cik, c, accn=accn, unit=unit):
            if r['end'] != end: continue
            if dur is None and r['dur'] is None: return r
            if dur is not None and r['dur'] is not None and abs(r['dur'] - dur) <= 8: return r
    return None
