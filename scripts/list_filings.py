import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edgar
CIKS = {'AAPL': 320193, 'PG': 80424, 'NVDA': 1045810, 'DFS': 1393612, 'HON': 773840, 'XOM': 34088, 'NKE': 320187}
for t, c in CIKS.items():
    fs = edgar.filings(c)
    print(f'--- {t} (CIK {c}) name={edgar.submissions(c)["name"]}  latest 10-K/10-Q:')
    for f in fs[:4]: print('   ', f['form'], 'period', f['period'], 'filed', f['filed'], f['accn'], f['doc'])
