import json,os,datetime as dt
FACTS=os.path.expanduser('~/didigou/autofinbench/repo/data/edgar/')
CIK={'HON':773840,'JNJ':200406,'PFE':78003,'T':732717,'AXP':4962,'TSLA':1318605,'KO':21344,'PG':80424,'AAPL':320193,'NKE':320187,'GIS':40704,'NVDA':1045810,'SPG':1063761,'FTNT':1262039,'HAL':45012,'SJM':91419,'CMS':811156,'XOM':34088,'NEE':753308}
_cache={}
def facts(t):
    if t not in _cache: _cache[t]=json.load(open(FACTS+f'facts_{CIK[t]}.json'))
    return _cache[t]
def series(t,concept,tax='us-gaap'):
    g=facts(t)['facts'].get(tax,{}).get(concept)
    if not g: return []
    out=[]
    for unit,xs in g['units'].items():
        for x in xs:
            r=dict(x); r['unit']=unit; r['concept']=concept; out.append(r)
    return out
def days(r):
    if not r.get('start'): return 0
    return (dt.date.fromisoformat(r['end'])-dt.date.fromisoformat(r['start'])).days
def annual(rows): return [r for r in rows if 350<=days(r)<=380 and r.get('form','').startswith('10-K')]
