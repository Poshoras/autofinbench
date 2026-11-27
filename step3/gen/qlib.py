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

