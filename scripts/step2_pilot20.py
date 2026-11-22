"""Pilot: rewrite 20 XFinBench seeds with controllable GT.

For every seed a small solver first reproduces the original XFinBench answer
(within 0.5%, the paper's tolerance); the rewritten item's GT comes from the
same solver with the changed condition. Operators:
  A condition switch, B reverse solve, C new numbers, D missing premise.
Usage: python3 -I scripts/step2_pilot20.py   (reads step2/seeds_200.jsonl)
"""
import json
import math

SEEDS = {json.loads(l)['id']: json.loads(l) for l in open('step2/seeds_200.jsonl')}


# ---------- generic finance helpers ----------
def bond_price(coupon_rate, face, ytm, years, m=1):
    k, i, n = coupon_rate * face / m, ytm / m, round(years * m)
    return k * (1 - (1 + i) ** -n) / i + face * (1 + i) ** -n


def solve(f, lo, hi, tol=1e-12):
    """Bisection; f(lo) and f(hi) must have opposite signs (checked)."""
    flo, fhi = f(lo), f(hi)
    assert flo * fhi < 0, 'root not bracketed'
    for _ in range(300):
        mid = (lo + hi) / 2
        fm = f(mid)
        if (fm < 0) == (flo < 0):
            lo, flo = mid, fm
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2


def binomial(S, K, r, T, steps, kind, american=False, u=None, d=None, sigma=None, q=0.0):
    dt = T / steps
    if u is None:
        u = math.exp(sigma * math.sqrt(dt)); d = 1 / u
    p = (math.exp((r - q) * dt) - d) / (u - d)
    disc = math.exp(-r * dt)
    pay = (lambda s: max(s - K, 0)) if kind == 'call' else (lambda s: max(K - s, 0))
    vals = [pay(S * u ** j * d ** (steps - j)) for j in range(steps + 1)]
    for n in range(steps - 1, -1, -1):
        vals = [disc * (p * vals[j + 1] + (1 - p) * vals[j]) for j in range(n + 1)]
        if american:
            vals = [max(v, pay(S * u ** j * d ** (n - j))) for j, v in enumerate(vals)]
    return vals[0]


def fv_annuity_factor(i, n):
    return ((1 + i) ** n - 1) / i


# ---------- the 20 items ----------
ITEMS = []


def item(**kw):
    ITEMS.append(kw)


# TR -----------------------------------------------------------------
item(id='test_63', op='B',
     repro=bond_price(.10, 1000, .1225, 8),
     convention='annual coupons (the semiannual reading gives 887.28, not 889.2)',
     new_q='A bond with a 10% coupon rate, paid annually, has a face value of $1,000 and eight years to maturity. '
           'It currently sells for $889.20.What is the bond\'s yield to maturity? (Unit: percent)',
     new_gt=100 * solve(lambda y: bond_price(.10, 1000, y, 8) - 889.20, .01, .5),
     change='已知价格 889.20，反求到期收益率（原题已知收益率求价格）',
     tests='反向求解：价格和收益率的关系只能迭代求解，不能直接代公式')

item(id='test_1091', op='B',
     repro=6000 * (1 + .084 / 365) ** (365 * 5),
     convention='daily compounding with 365 days per year',
     new_q='Corpstein Credit Bank is offering 8.4 percent compounded daily on its savings accounts, with 365 days per year. '
           'Suppose you deposit $6,000 today.How many years will it take for the balance to reach $9,131.33? (Unit: years)',
     new_gt=math.log(9131.33 / 6000) / (365 * math.log(1 + .084 / 365)),
     change='已知终值，反求年数（原题已知年数求终值）',
     tests='反向求解：要对复利公式取对数')

r_m = .11 / 12
pay_end = 1e6 / fv_annuity_factor(r_m, 240)
r_ear = 1.11 ** (1 / 12) - 1
item(id='test_3073', op='A',
     repro=pay_end,
     convention='11% is an APR compounded monthly; deposits at the end of each month',
     new_q='You want to be a millionaire when you retire in 40 years. Assume you can earn an 11 percent effective annual '
           'return (EAR) on your savings. You wait 20 years before you begin, and then make equal deposits at the end of each '
           'month for the remaining 20 years.How much do you have to save each month? (Unit: dollar)',
     new_gt=1e6 / fv_annuity_factor(r_ear, 240),
     naive=pay_end,
     change='"年回报 11%" 明确为有效年利率（EAR），原题按名义年利率除以 12',
     tests='条件切换：月利率要用 1.11^(1/12)−1，不能用 11%/12。最初试的是"月末改月初存款"，'
           '新旧答案只差 0.9%，离 0.5% 容差太近，所以换成这个')


def spears(r):
    return sum(div / (1 + r) ** t for t, div in enumerate([11, 15, 19, 23], start=1))


item(id='test_2545', op='B',
     repro=spears(.11),
     convention='dividends of 11, 15, 19, 23 in years 1-4, then nothing',
     new_q='Spears, Inc., has an odd dividend policy. The company has just paid a dividend of $7 per share and has announced '
           'that it will increase the dividend by $4 per share for each of the next four years, and then never pay another '
           'dividend. The stock currently sells for $51.13.What is the required return implied by the stock price? (Unit: percent)',
     new_gt=100 * solve(lambda r: spears(r) - 51.13, .001, 1),
     change='已知股价 51.13，反求必要回报率（原题已知回报率求股价）',
     tests='反向求解：要自己列出 4 年的股利再迭代求贴现率')

item(id='test_2275', op='A',
     repro=31 / 180 * 3.5,
     convention='corporate bonds use 30/360: 31 days of a 180-day half-year (actual/actual would give 0.6087)',
     new_q='A U.S. Treasury bond pays a 7% coupon on January 7 and July 7.How much interest accrues per $100 of principal '
           'on the Treasury bond between January 7, 2015, and March 1, 2015? (Unit: dollar)',
     new_gt=53 / 181 * 3.5,
     naive=54 / 180 * 3.5,
     change='公司债改成美国国债；计息区间改成 2015-01-07 到 2015-03-01',
     tests='条件切换：国债按实际天数/实际天数计息（53/181），公司债按 30/360（54/180）。考的是行业惯例知识。'
           '区间也换了：原区间下两种算法只差 0.98%，跨 2 月的区间差 2.4%')

# SP; TR -------------------------------------------------------------
item(id='test_1102', op='A',
     repro=binomial(40, 42, .12, .5, 2, 'put', u=1.1, d=.9),
     convention='two-step tree, u=1.1, d=0.9, three-month steps',
     new_q='A stock price is currently $40. Over each of the next three three-month periods, it is expected to go up by 10% '
           'or down by 10%. The risk-free interest rate is 6% per annum with continuous compounding.What is the value of a '
           'nine-month American put option with a strike price of $42? (Unit: dollar)',
     new_gt=binomial(40, 42, .06, .75, 3, 'put', american=True, u=1.1, d=.9),
     naive=binomial(40, 42, .06, .75, 3, 'put', u=1.1, d=.9),
     change='欧式看跌改成美式看跌，两步树延长为三步（九个月），利率从 12% 改成 6%',
     tests='条件切换：要在每个节点比较立即行权和继续持有，这正是论文中 o1 犯的错。'
           '只改成美式不够：XFinBench 里已有这道兄弟题（test_2575，答案 2.537）。改成三步、利率仍为 12% 时，'
           '第 2 步各节点都提前行权，答案恰好也是 2.537，所以利率也改了')

item(id='test_1716', op='C',
     repro=binomial(78, 80, .03, 4 / 12, 2, 'call', sigma=.30),
     convention='CRR tree u=exp(sigma*sqrt(dt)), dt = 2 months',
     new_q='The volatility of a non-dividend-paying stock, whose price is $60, is 25%. The risk-free rate is 4% per annum '
           '(continuously compounded) for all maturities. A two-month time step is used for calculations.What is the value '
           'of a four-month European call option with a strike price of $62 given by a two-step binomial tree? (Unit: dollar)',
     new_gt=binomial(60, 62, .04, 4 / 12, 2, 'call', sigma=.25),
     change='股价、波动率、利率、行权价都换了新数值，题型不变',
     tests='换数字：检查模型是不是背过原题答案（污染对照），不是为了变难')

# SP -----------------------------------------------------------------
p1822 = (math.exp(.08 / 12) - 38 / 40) / (42 / 40 - 38 / 40)
item(id='test_1822', op='D',
     repro=math.exp(-.08 / 12) * p1822 * 3,
     convention='one-step no-arbitrage valuation',
     new_q='A stock price is currently $40. At the end of one month, it will be either $42 or $38.What is the value of a '
           'one-month European call option with a strike price of $39? (Unit: dollar)',
     new_gt='NOT ANSWERABLE: the risk-free interest rate is missing',
     naive=0.5 * 3,
     change='删掉无风险利率',
     tests='缺前提：无套利定价必须用到无风险利率，其余数字推不出它。应回答算不出，并指出缺的是利率；如果默认利率为 0 硬算出 1.50，判错')

item(id='test_1137', op='A',
     repro=28 - 25 * math.exp(-.08 * 4 / 12),
     convention='lower bound S - K e^{-rT}',
     new_q='A four-month European call option on a stock has a stock price of $28, a strike price of $25, and the risk-free '
           'interest rate is 8% per annum with continuous compounding. A dividend of $1.00 per share is expected in two '
           'months.What is a lower bound for the price of the call option? (Unit: dollar)',
     new_gt=28 - 1.00 * math.exp(-.08 * 2 / 12) - 25 * math.exp(-.08 * 4 / 12),
     naive=28 - 25 * math.exp(-.08 * 4 / 12),
     change='无分红改成两个月后分红 1 美元',
     tests='条件切换：下界要减去分红的现值。原题写的是 non-dividend-paying，新题去掉了这一句')

item(id='test_1907', op='A',
     repro=400 * math.exp((.10 - .04) * 4 / 12),
     convention='continuous compounding: F = S e^{(r-q)T}',
     new_q='Suppose that the risk-free interest rate is 10% per annum and that the dividend yield on a stock index is 4% per '
           'annum, both expressed with annual compounding. The index is standing at 400.What is the theoretical forward price '
           'for a contract deliverable in three years? (Unit: dollar)',
     new_gt=400 * (1.10 / 1.04) ** 3,
     naive=400 * math.exp((.10 - .04) * 3),
     change='连续复利改成年复利，期限从四个月改成三年',
     tests='条件切换：e^{(r−q)T} 要换成 ((1+r)/(1+q))^T。四个月期限下两种算法只差 0.13%，在容差内分不开，'
           '所以拉长到三年（差 1.2%）。同时删掉了原题里"市场期货价 405"这个与问题无关的数')

item(id='test_2667', op='A',
     repro=round((1.2 - .6) * 20e6 / (1080 * 250)),
     naive=-round((1.5 - 1.2) * 20e6 / (1080 * 250)),
     convention='N = (beta - beta*) P / (F x 250), rounded to whole contracts (44.44 -> 44)',
     new_q='A company has a $20 million portfolio with a beta of 1.2. It would like to use futures contracts on a stock index '
           'to change its exposure. The index futures is currently standing at 1080, and each contract is for delivery of $250 '
           'times the index.How many futures contracts should the company trade to increase the portfolio\'s beta to 1.5? '
           'Give a positive number for a long position and a negative number for a short position, rounded to the nearest '
           'whole contract. (Unit: contract)',
     new_gt=round((1.5 - 1.2) * 20e6 / (1080 * 250)),
     change='把 beta 从 1.2 降到 0.6，改成从 1.2 升到 1.5',
     tests='条件切换：方向反了，要做多而不是做空。题干要求用正负号表示方向')

# TU -----------------------------------------------------------------
item(id='test_95', op='D',
     repro=(3000 - 2000) / 5000 * 100,
     convention='margin call when losses exceed initial minus maintenance margin',
     new_q='A company enters into a short futures contract to sell 5,000 bushels of wheat for 750 cents per bushel. The initial '
           'margin is $3,000.What price change would lead to a margin call? (Unit: cents per bushel)',
     new_gt='NOT ANSWERABLE: the maintenance margin is missing',
     change='删掉维持保证金',
     tests='缺前提：追加保证金的触发点由维持保证金决定，只有初始保证金推不出来。按"常见比例 75%"估一个数判错')

item(id='test_2192', op='A',
     repro=60 / 1.05,
     convention='stock dividend: strike divided by 1.05',
     new_q='A trader has an exchange-traded put option contract to sell 100 shares of a stock for a strike price of $60. The '
           'stock trades at $65, and the company pays its regular quarterly cash dividend of $2.00 per share.What is the '
           'strike price of the contract after the dividend? (Unit: dollar)',
     new_gt=60.0,
     naive=60 - 2.0,
     change='5% 股票股利改成普通的季度现金股利（2 美元，约为股价的 3%）',
     tests='条件切换（陷阱）：交易所期权不因普通现金股利调整条款（大额现金股利才调整，一般指超过股价 10%），'
           '答案仍是 60。把股利从行权价里扣掉得 58，判错')

# FF -----------------------------------------------------------------
item(id='test_945', op='A',
     repro=1e6 / (.10 + .10),
     convention='deposit multiplier 1/(rr + e)',
     new_q='The Fed buys $1 million of bonds from the First National Bank. The required reserve ratio on checkable deposits '
           'is 10%, banks hold an additional 10% of deposits as excess reserves, and the public holds currency equal to 20% of '
           'its checkable deposits.What is the total increase in checkable deposits? (Unit: dollar)',
     new_gt=1e6 / (.10 + .10 + .20),
     naive=1e6 / (.10 + .10),
     change='加入公众持有现金（占存款 20%）',
     tests='条件切换：存款乘数变成 1/(rr+e+c)，基础货币有一部分流到银行体系外')

item(id='test_2997', op='C',
     repro=(30e6 - 20e6) * .05,
     convention='income gap = (RSA - RSL) x change in rate',
     new_q='You are the manager of a bank that has $20 million of fixed-rate assets, $25 million of rate-sensitive assets, '
           '$15 million of fixed-rate liabilities, and $30 million of rate-sensitive liabilities.What will be the change in bank '
           'profits if interest rates rise by 3 percentage points? (Unit: dollar)',
     new_gt=(25e6 - 30e6) * .03,
     change='换数字，使利率敏感负债大于利率敏感资产',
     tests='换数字：缺口由正变负，加息后利润下降，答案为负')

# NM -----------------------------------------------------------------
def wacc(de, re=.17, rd=.10, t=.35):
    return re / (1 + de) + rd * (1 - t) * de / (1 + de)


item(id='test_171', op='B',
     repro=wacc(.80),
     convention='weights from D/E: D/V = 0.8/1.8',
     new_q='Cookie Dough Manufacturing has a cost of equity of 17 percent and a pretax cost of debt of 10 percent. The tax rate '
           'is 35 percent. The company\'s WACC is 12.33 percent.What target debt-equity ratio is the company using? (Unit: decimal)',
     new_gt=solve(lambda x: wacc(x) - .1233, 0, 5),
     change='已知 WACC，反求负债权益比',
     tests='反向求解：要从 D/E 推权重，再解方程。GT 为 0.801（WACC 只给到两位小数，所以不是正好 0.80）')

vu = 12000 * (1 - .35) / .16
item(id='test_2281', op='A',
     repro=vu + .35 * .5 * vu,
     convention='debt = 50% of the unlevered value (V_L = V_U + T_c D); reading "50% of levered value" gives 59,090.91',
     new_q='Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt, and its cost '
           'of equity is 16 percent. The firm can borrow at 9 percent. There are no corporate or personal taxes, and capital '
           'markets are perfect.What will the value of the firm be if Old School converts to 50 percent debt? (Unit: dollar)',
     new_gt=12000 / .16,
     naive=vu + .35 * .5 * vu,
     change='有公司税改成无税',
     tests='条件切换（陷阱）：无税时 MM 定理第一条成立，杠杆不改变公司价值，答案就是无负债时的价值 75,000。'
           '顺带消除了原题"50% 负债"指哪种价值的歧义')

item(id='test_1856', op='C',
     repro=math.sqrt(2 * 2500 * 52 * 2400 / 10),
     convention='52 weeks per year; carrying cost is per unit per year',
     new_q='Redan Manufacturing uses 1,800 switch assemblies per week and then reorders another 1,800. The relevant carrying '
           'cost per switch assembly is $6 per year, and the fixed order cost is $1,500. Assume 52 weeks per year.What is the '
           'economic order quantity (EOQ)? (Unit: assembly)',
     new_gt=math.sqrt(2 * 1800 * 52 * 1500 / 6),
     change='每周用量、持有成本、订货成本都换了新数值',
     tests='换数字：污染对照。题干补写了"每年 52 周"和"持有成本按年计"，原题没写')

# NM; SP -------------------------------------------------------------
be = solve(lambda e: (e - 2000) / 1500 - (e - 3000) / 1100, 0, 1e6)
item(id='test_1506', op='B',
     repro=be,
     convention='EPS_I = (EBIT - 2,000)/1,500, EPS_II = (EBIT - 3,000)/1,100',
     new_q='Kolby Corp. is comparing two different capital structures, Plan I and Plan II. Plan I would result in 1,500 shares '
           'of stock and $20,000 in debt, while Plan II would result in 1,100 shares of stock. The interest rate on the debt is '
           '10 percent. Ignore taxes.How much debt would Plan II need for EPS under the two plans to be identical when EBIT is '
           '$5,750? (Unit: dollar)',
     new_gt=solve(lambda D: (5750 - 2000) / 1500 - (5750 - .10 * D) / 1100, 0, 1e6),
     change='已知盈亏平衡 EBIT 5,750，反求 Plan II 的负债额',
     tests='反向求解：先算出 Plan I 在该 EBIT 下的 EPS，再倒推 Plan II 的利息和负债。'
           '最初试的是"加 40% 公司税"：盈亏平衡点不变，忽略税的模型也能答对，题目区分不了，所以放弃')

# NM; TR -------------------------------------------------------------
item(id='test_2972', op='A',
     repro=865 + 75 / 2 * (3 / 6),
     convention='semiannual coupon 37.5; half of the period has elapsed',
     new_q='You purchase a bond with a coupon rate of 7.5 percent, a face value of $1,000 and a clean price of $865. The bond '
           'pays its coupon once a year, and the next annual coupon payment is due in three months.What is the invoice price of '
           'the bond? (Unit: dollar)',
     new_gt=865 + 75 * (9 / 12),
     naive=865 + 75 / 2 * (3 / 6),
     change='半年付息改成一年付息',
     tests='条件切换：应计利息变成一整年息票的 9/12，而不是半年息票的一半')


def main():
    out, bad = [], []
    for it in ITEMS:
        s = SEEDS[it['id']]
        gt = float(s['ground_truth'])
        ok = abs(it['repro'] - gt) <= 0.005 * abs(gt)
        if not ok:
            bad.append((it['id'], it['repro'], gt))
        new_gt = it['new_gt'] if isinstance(it['new_gt'], str) else round(it['new_gt'], 4)
        naive = it.get('naive', gt if it['op'] == 'C' else None)
        gap = None
        if naive is not None and not isinstance(it['new_gt'], str):
            gap = round(100 * abs(it['new_gt'] - naive) / abs(it['new_gt']), 2)
            if gap < 1.0:
                bad.append((it['id'], 'old-method answer within 1% of new GT', gap))
        out.append(dict(id=it['id'], fin_capability=s['fin_capability'], topic=s['topic'], op=it['op'],
                        original_question=s['question'], original_gt=gt, reproduced=round(it['repro'], 4),
                        reproduced_ok=ok, convention_used=it['convention'],
                        new_question=it['new_q'], new_gt=new_gt,
                        old_method_answer=None if naive is None else round(naive, 4), gap_vs_old_method_pct=gap,
                        change=it['change'], tests=it['tests']))
    with open('step2/pilot20.jsonl', 'w') as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(len(out), 'items; problems:', bad)
    for r in out:
        print(r['id'], r['op'], r['fin_capability'], 'orig', r['original_gt'], 'repro', r['reproduced'], 'new', r['new_gt'], 'old-method', r['old_method_answer'], 'gap%', r['gap_vs_old_method_pct'])


if __name__ == '__main__':
    main()


OPS = {'A': 'A 条件切换', 'B': 'B 反向求解', 'C': 'C 换数字', 'D': 'D 缺前提'}


def fmt(x):
    if isinstance(x, str):
        return x
    return f'{x:,.4f}'.rstrip('0').rstrip('.')


def write_md(path='step2/pilot20_items.md'):
    P = [json.loads(l) for l in open('step2/pilot20.jsonl')]
    lines = ['# 20 道改写题（逐题）', '',
             '由 `scripts/step2_pilot20.py` 生成。每道题：原题 → 用程序复现原答案 → 改写 → 用同一程序算新答案。',
             '"旧方法得数"：模型如果没注意到改动、照原题方法做，会得到这个数；它和新答案至少差 1%，所以会被判错。', '']
    for k, r in enumerate(P, 1):
        lines += [f"## {k}. {r['id']}　{r['fin_capability']}　{OPS[r['op']]}", '',
                  f"**原题**：{r['original_question']}", '',
                  f"原答案 {fmt(r['original_gt'])}；程序复现 {fmt(r['reproduced'])}（{r['convention_used']}）", '',
                  f"**新题**：{r['new_question']}", '',
                  f"**新答案**：{fmt(r['new_gt'])}", '',
                  f"- 改了什么：{r['change']}",
                  f"- 考什么：{r['tests']}"]
        if r['old_method_answer'] is not None:
            tag = '（若作答即判错）' if r['op'] == 'D' else f"，与新答案差 {r['gap_vs_old_method_pct']}%"
            lines.append(f"- 旧方法得数：{fmt(r['old_method_answer'])}{tag}")
        lines.append('')
    open(path, 'w').write('\n'.join(lines))


write_md()
