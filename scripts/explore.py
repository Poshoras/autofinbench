import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xbrl
cik, accn = int(sys.argv[1]), sys.argv[2]
for c in sys.argv[3:]:
    rows = xbrl.facts(cik, c, accn=accn)
    rows = sorted({(r['concept'], r.get('start',''), r['end'], r['dur'], r['val'], r['unit']) for r in rows}, key=lambda x:(x[2],x[1]))
    print(f'## {c}: {len(rows)} facts')
    for r in rows[-8:]: print('   ', r[1] or '(instant)', '->', r[2], f'dur={r[3]}', f'{r[4]:,}', r[5])
