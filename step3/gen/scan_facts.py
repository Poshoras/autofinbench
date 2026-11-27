import json,glob,os,collections,sys
rows=[]
for f in sorted(glob.glob(os.path.expanduser('~/didigou/autofinbench/repo/data/edgar/facts_*.json'))):
    d=json.load(open(f)); name=d.get('entityName'); cik=d.get('cik')
    g=d['facts'].get('us-gaap',{})
    maxfiled=max((x['filed'] for c in g.values() for u in c['units'].values() for x in u),default='')
    # restatements: same concept, same start/end, FY duration, different val across filings
    rest=0; ex=[]
    for cname in ['Revenues','RevenueFromContractWithCustomerExcludingAssessedTax','NetIncomeLoss','OperatingIncomeLoss','CostOfRevenue','GrossProfit','NetCashProvidedByUsedInOperatingActivities','Assets','StockholdersEquity']:
        if cname not in g: continue
        for unit,xs in g[cname]['units'].items():
            by=collections.defaultdict(set)
            for x in xs:
                if x.get('form') not in ('10-K','10-K/A','10-Q','10-Q/A'): continue
                by[(x.get('start'),x['end'])].add((x['val'],))
            for k,v in by.items():
                if len(v)>1 and k[1]>='2021-01-01':
                    rest+=1
                    if len(ex)<2: ex.append((cname,k,sorted(v)))
    print(cik,name[:28],'maxfiled',maxfiled,'restated_keys',rest,ex[:1])
