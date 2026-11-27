import csv,json,os
E=os.path.expanduser('~/didigou/autofinbench/repo/step3/env/')
def load(q,n='facts.csv'): return list(csv.DictReader(open(E+q+'/'+n)))
def pick(rows,c,start,end,asof=None,accn=None):
    rs=[r for r in rows if r['concept']==c and r['start']==start and r['end']==end and r['form'].startswith('10-K') and (asof is None or r['filed']<=asof) and (accn is None or r['accn']==accn)]
    rs.sort(key=lambda r:r['filed']); return float(rs[-1]['val'])/1e6 if rs else None
R='RevenueFromContractWithCustomerExcludingAssessedTax';O='OperatingIncomeLoss';C='NetCashProvidedByUsedInOperatingActivities';X='PaymentsToAcquirePropertyPlantAndEquipment'
f=load('q001');a='2025-06-30'
r24,r23,o24=pick(f,R,'2024-01-01','2024-12-31',a),pick(f,R,'2023-01-01','2023-12-31',a),pick(f,O,'2024-01-01','2024-12-31',a)
out={'q001':{'revenue_growth_pct':(r24/r23-1)*100,'operating_margin_pct':o24/r24*100,'fcf_usd_m':pick(f,C,'2024-01-01','2024-12-31',a)-pick(f,X,'2024-01-01','2024-12-31',a)}}
f=load('q002');a='2026-11-15'
r25,r24,o25=pick(f,R,'2025-01-01','2025-12-31',a),pick(f,R,'2024-01-01','2024-12-31',a),pick(f,O,'2025-01-01','2025-12-31',a)
out['q002']={'revenue_growth_pct':(r25/r24-1)*100,'operating_margin_pct':o25/r25*100,'fcf_usd_m':pick(f,C,'2025-01-01','2025-12-31',a)-pick(f,X,'2025-01-01','2025-12-31',a),'fy2024_revenue_used_usd_m':r24}
f=load('q003');E_='EarningsPerShareDiluted'
e24o=[r for r in f if r['concept']==E_ and r['end']=='2024-01-28' and r['form']=='10-K'];e24o.sort(key=lambda r:r['filed'])
e26=[r for r in f if r['concept']==E_ and r['end']=='2026-01-25' and r['form']=='10-K'][0]
out['q003']={'eps_fy2024_as_reported':float(e24o[0]['val']),'eps_fy2024_comparable':float(e24o[-1]['val']),'eps_cagr_pct':((float(e26['val'])/float(e24o[-1]['val']))**0.5-1)*100}
f=load('q005')
oc=pick(f,C,'2025-05-26','2026-05-31');cx=pick(f,X,'2025-05-26','2026-05-31');rv=pick(f,R,'2025-05-26','2026-05-31')
out['q005']={'fcf_usd_m':oc-cx,'fcf_margin_pct':(oc-cx)/rv*100}
f=load('q004');out['q004_capex_fy2026_present']=pick(f,X,'2025-07-01','2026-06-30') is not None
f=load('q006','fy2025_10k_facts.csv');ac='0000773840-26-000013'
out['q006']={'rev24':pick(f,R,'2024-01-01','2024-12-31',accn=ac),'capex24':pick(f,X,'2024-01-01','2024-12-31',accn=ac),'eps25':[r['val'] for r in f if r['concept']=='EarningsPerShareDiluted' and r['end']=='2025-12-31']}
for q,v in out.items():
    if isinstance(v,dict) and q!='q006':
        g=json.load(open(f'gt/{q}.json'))['fields']
        print(q,'OK' if all(abs(v[k]-g[k])<1e-6 for k in v) else ('MISMATCH',v,g))
    else: print(q,v)
