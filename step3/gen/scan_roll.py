from lib import *
import collections
cands=['Revenues','RevenueFromContractWithCustomerExcludingAssessedTax','OperatingIncomeLoss','NetIncomeLoss','CostOfRevenue','CostOfGoodsAndServicesSold','ResearchAndDevelopmentExpense','SellingGeneralAndAdministrativeExpense','NetCashProvidedByUsedInOperatingActivities','PaymentsToAcquirePropertyPlantAndEquipment','IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest','EarningsPerShareDiluted']
for t in CIK:
    hits=[]
    for c in cands:
        rows=annual(series(t,c))
        by=collections.defaultdict(list)
        for r in rows: by[r['end']].append(r)
        for end,rs in by.items():
            if not ('2023-06'<=end<='2025-12-31'): continue
            vals={}
            for r in rs: vals.setdefault(r['val'],min(vals.get(r['val'],'9'),r['filed']))
            if len(vals)>1: hits.append((c,end,sorted(vals.items(),key=lambda kv:kv[1])))
    if hits: print(t,len(hits),[ (h[0][:22],h[1],h[2]) for h in hits[:3]])
