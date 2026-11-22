# 20 道改写题（逐题）

由 `scripts/step2_pilot20.py` 生成。每道题：原题 → 用程序复现原答案 → 改写 → 用同一程序算新答案。
"旧方法得数"：模型如果没注意到改动、照原题方法做，会得到这个数；它和新答案至少差 1%，所以会被判错。

## 1. test_63　TR　B 反向求解

**原题**：A 10% coupon bond has a face value of $1000, a 12.25% yield to maturity, and eight years to maturity.What is the price of the bond? (Unit: dollar)

原答案 889.2；程序复现 889.1977（annual coupons (the semiannual reading gives 887.28, not 889.2)）

**新题**：A bond with a 10% coupon rate, paid annually, has a face value of $1,000 and eight years to maturity. It currently sells for $889.20.What is the bond's yield to maturity? (Unit: percent)

**新答案**：12.2499

- 改了什么：已知价格 889.20，反求到期收益率（原题已知收益率求价格）
- 考什么：反向求解：价格和收益率的关系只能迭代求解，不能直接代公式

## 2. test_1091　TR　B 反向求解

**原题**：Corpstein Credit Bank is offering 8.4 percent compounded daily on its savings accounts. Suppose you deposit $6,000 today.How much will you have in the account in 5 years? (Unit: dollar)

原答案 9,131.33；程序复现 9,131.3281（daily compounding with 365 days per year）

**新题**：Corpstein Credit Bank is offering 8.4 percent compounded daily on its savings accounts, with 365 days per year. Suppose you deposit $6,000 today.How many years will it take for the balance to reach $9,131.33? (Unit: years)

**新答案**：5

- 改了什么：已知终值，反求年数（原题已知年数求终值）
- 考什么：反向求解：要对复利公式取对数

## 3. test_3073　TR　A 条件切换

**原题**：You want to be a millionaire when you retire in 40 years. Assume you can earn an 11 percent annual return from your savings, and you consider making monthly deposits.How much do you have to save each month to be a millionaire if you wait 20 years before you begin your deposits? (Unit: dollar)

原答案 1,155.22；程序复现 1,155.2173（11% is an APR compounded monthly; deposits at the end of each month）

**新题**：You want to be a millionaire when you retire in 40 years. Assume you can earn an 11 percent effective annual return (EAR) on your savings. You wait 20 years before you begin, and then make equal deposits at the end of each month for the remaining 20 years.How much do you have to save each month? (Unit: dollar)

**新答案**：1,236.7897

- 改了什么："年回报 11%" 明确为有效年利率（EAR），原题按名义年利率除以 12
- 考什么：条件切换：月利率要用 1.11^(1/12)−1，不能用 11%/12。最初试的是"月末改月初存款"，新旧答案只差 0.9%，离 0.5% 容差太近，所以换成这个
- 旧方法得数：1,155.2173，与新答案差 6.6%

## 4. test_2545　TR　B 反向求解

**原题**：Spears, Inc., has an odd dividend policy. The company has just paid a dividend of $7 per share and has announced that it will increase the dividend by $4 per share for each of the next four years, and then never pay another dividend. The required return on the company's stock is 11 percent.How much will you pay for a share of Spears, Inc. today? (Unit: dollar)

原答案 51.13；程序复现 51.1277（dividends of 11, 15, 19, 23 in years 1-4, then nothing）

**新题**：Spears, Inc., has an odd dividend policy. The company has just paid a dividend of $7 per share and has announced that it will increase the dividend by $4 per share for each of the next four years, and then never pay another dividend. The stock currently sells for $51.13.What is the required return implied by the stock price? (Unit: percent)

**新答案**：10.9981

- 改了什么：已知股价 51.13，反求必要回报率（原题已知回报率求股价）
- 考什么：反向求解：要自己列出 4 年的股利再迭代求贴现率

## 5. test_2275　TR　A 条件切换

**原题**：A corporate bond pays a 7% coupon on January 7 and July 7. The time frame is between July 7, 2014, and August 8, 2014.How much interest accrues per $100 of principal for a corporate bond between July 7, 2014, and August 8, 2014? (Unit: dollar)

原答案 0.6028；程序复现 0.6028（corporate bonds use 30/360: 31 days of a 180-day half-year (actual/actual would give 0.6087)）

**新题**：A U.S. Treasury bond pays a 7% coupon on January 7 and July 7.How much interest accrues per $100 of principal on the Treasury bond between January 7, 2015, and March 1, 2015? (Unit: dollar)

**新答案**：1.0249

- 改了什么：公司债改成美国国债；计息区间改成 2015-01-07 到 2015-03-01
- 考什么：条件切换：国债按实际天数/实际天数计息（53/181），公司债按 30/360（54/180）。考的是行业惯例知识。区间也换了：原区间下两种算法只差 0.98%，跨 2 月的区间差 2.4%
- 旧方法得数：1.05，与新答案差 2.45%

## 6. test_1102　SP; TR　A 条件切换

**原题**：A stock price is currently $40. Over each of the next two three-month periods, it is expected to go up by 10% or down by 10%. The risk-free interest rate is 12% per annum with continuous compounding.What is the value of a six-month European put option with a strike price of $42? (Unit: dollar)

原答案 2.118；程序复现 2.1185（two-step tree, u=1.1, d=0.9, three-month steps）

**新题**：A stock price is currently $40. Over each of the next three three-month periods, it is expected to go up by 10% or down by 10%. The risk-free interest rate is 6% per annum with continuous compounding.What is the value of a nine-month American put option with a strike price of $42? (Unit: dollar)

**新答案**：3.1391

- 改了什么：欧式看跌改成美式看跌，两步树延长为三步（九个月），利率从 12% 改成 6%
- 考什么：条件切换：要在每个节点比较立即行权和继续持有，这正是论文中 o1 犯的错。只改成美式不够：XFinBench 里已有这道兄弟题（test_2575，答案 2.537）。改成三步、利率仍为 12% 时，第 2 步各节点都提前行权，答案恰好也是 2.537，所以利率也改了
- 旧方法得数：2.8298，与新答案差 9.85%

## 7. test_1716　SP; TR　C 换数字

**原题**：The volatility of a non-dividend-paying stock, whose price is $78, is 30%. The risk-free rate is 3% per annum (continuously compounded) for all maturities. A two-month time step is used for calculations.What is the value of a four-month European call option with a strike price of $80 given by a two-step binomial tree? (Unit: dollar)

原答案 4.67；程序复现 4.6677（CRR tree u=exp(sigma*sqrt(dt)), dt = 2 months）

**新题**：The volatility of a non-dividend-paying stock, whose price is $60, is 25%. The risk-free rate is 4% per annum (continuously compounded) for all maturities. A two-month time step is used for calculations.What is the value of a four-month European call option with a strike price of $62 given by a two-step binomial tree? (Unit: dollar)

**新答案**：2.9415

- 改了什么：股价、波动率、利率、行权价都换了新数值，题型不变
- 考什么：换数字：检查模型是不是背过原题答案（污染对照），不是为了变难
- 旧方法得数：4.67，与新答案差 58.76%

## 8. test_1822　SP　D 缺前提

**原题**：A stock price is currently $40. At the end of one month, it will be either $42 or $38. The risk-free interest rate is 8% per annum with continuous compounding.What is the value of a one-month European call option with a strike price of $39? (Unit: dollar)

原答案 1.69；程序复现 1.6894（one-step no-arbitrage valuation）

**新题**：A stock price is currently $40. At the end of one month, it will be either $42 or $38.What is the value of a one-month European call option with a strike price of $39? (Unit: dollar)

**新答案**：NOT ANSWERABLE: the risk-free interest rate is missing

- 改了什么：删掉无风险利率
- 考什么：缺前提：无套利定价必须用到无风险利率，其余数字推不出它。应回答算不出，并指出缺的是利率；如果默认利率为 0 硬算出 1.50，判错
- 旧方法得数：1.5（若作答即判错）

## 9. test_1137　SP　A 条件切换

**原题**：A four-month call option on a non-dividend-paying stock has a stock price of $28, a strike price of $25, and the risk-free interest rate is 8% per annum.What is a lower bound for the price of the call option? (Unit: dollar)

原答案 3.66；程序复现 3.6579（lower bound S - K e^{-rT}）

**新题**：A four-month European call option on a stock has a stock price of $28, a strike price of $25, and the risk-free interest rate is 8% per annum with continuous compounding. A dividend of $1.00 per share is expected in two months.What is a lower bound for the price of the call option? (Unit: dollar)

**新答案**：2.6711

- 改了什么：无分红改成两个月后分红 1 美元
- 考什么：条件切换：下界要减去分红的现值。原题写的是 non-dividend-paying，新题去掉了这一句
- 旧方法得数：3.6579，与新答案差 36.94%

## 10. test_1907　SP　A 条件切换

**原题**：Suppose that the risk-free interest rate is 10% per annum with continuous compounding and that the dividend yield on a stock index is 4% per annum. The index is standing at 400, and the futures price for a contract deliverable in four months is 405.What is the theoretical futures price for a contract deliverable in four months? (Unit: dollar)

原答案 408.08；程序复现 408.0805（continuous compounding: F = S e^{(r-q)T}）

**新题**：Suppose that the risk-free interest rate is 10% per annum and that the dividend yield on a stock index is 4% per annum, both expressed with annual compounding. The index is standing at 400.What is the theoretical forward price for a contract deliverable in three years? (Unit: dollar)

**新答案**：473.3017

- 改了什么：连续复利改成年复利，期限从四个月改成三年
- 考什么：条件切换：e^{(r−q)T} 要换成 ((1+r)/(1+q))^T。四个月期限下两种算法只差 0.13%，在容差内分不开，所以拉长到三年（差 1.2%）。同时删掉了原题里"市场期货价 405"这个与问题无关的数
- 旧方法得数：478.8869，与新答案差 1.18%

## 11. test_2667　SP　A 条件切换

**原题**：A company has a $20 million portfolio with a beta of 1.2. It would like to use futures contracts on a stock index to hedge its risk. The index futures is currently standing at 1080, and each contract is for delivery of $250 times the index.How many futures contracts should be shorted to reduce the portfolio's beta to 0.6? (Unit: contract)

原答案 44；程序复现 44（N = (beta - beta*) P / (F x 250), rounded to whole contracts (44.44 -> 44)）

**新题**：A company has a $20 million portfolio with a beta of 1.2. It would like to use futures contracts on a stock index to change its exposure. The index futures is currently standing at 1080, and each contract is for delivery of $250 times the index.How many futures contracts should the company trade to increase the portfolio's beta to 1.5? Give a positive number for a long position and a negative number for a short position, rounded to the nearest whole contract. (Unit: contract)

**新答案**：22

- 改了什么：把 beta 从 1.2 降到 0.6，改成从 1.2 升到 1.5
- 考什么：条件切换：方向反了，要做多而不是做空。题干要求用正负号表示方向
- 旧方法得数：-22，与新答案差 200.0%

## 12. test_95　TU　D 缺前提

**原题**：A company enters into a short futures contract to sell 5,000 bushels of wheat for 750 cents per bushel. The initial margin is $3,000 and the maintenance margin is $2,000.What price change would lead to a margin call? (Unit: cents per bushel)

原答案 20；程序复现 20（margin call when losses exceed initial minus maintenance margin）

**新题**：A company enters into a short futures contract to sell 5,000 bushels of wheat for 750 cents per bushel. The initial margin is $3,000.What price change would lead to a margin call? (Unit: cents per bushel)

**新答案**：NOT ANSWERABLE: the maintenance margin is missing

- 改了什么：删掉维持保证金
- 考什么：缺前提：追加保证金的触发点由维持保证金决定，只有初始保证金推不出来。按"常见比例 75%"估一个数判错

## 13. test_2192　TU　A 条件切换

**原题**：A trader has a put option contract to sell 100 shares of a stock for a strike price of $60.What is the effect on the terms of the contract if a 5% stock dividend is paid regarding the new strike price? (Unit: dollar)

原答案 57.14；程序复现 57.1429（stock dividend: strike divided by 1.05）

**新题**：A trader has an exchange-traded put option contract to sell 100 shares of a stock for a strike price of $60. The stock trades at $65, and the company pays its regular quarterly cash dividend of $2.00 per share.What is the strike price of the contract after the dividend? (Unit: dollar)

**新答案**：60

- 改了什么：5% 股票股利改成普通的季度现金股利（2 美元，约为股价的 3%）
- 考什么：条件切换（陷阱）：交易所期权不因普通现金股利调整条款（大额现金股利才调整，一般指超过股价 10%），答案仍是 60。把股利从行权价里扣掉得 58，判错
- 旧方法得数：58，与新答案差 3.33%

## 14. test_945　FF　A 条件切换

**原题**：If the Fed buys $1 million of bonds from the First National Bank, and an additional 10% of any deposit is held as excess reserves, the reserve requirement ratio is 10%.What is the total increase in checkable deposits? (Unit: dollar)

原答案 5,000,000；程序复现 5,000,000（deposit multiplier 1/(rr + e)）

**新题**：The Fed buys $1 million of bonds from the First National Bank. The required reserve ratio on checkable deposits is 10%, banks hold an additional 10% of deposits as excess reserves, and the public holds currency equal to 20% of its checkable deposits.What is the total increase in checkable deposits? (Unit: dollar)

**新答案**：2,500,000

- 改了什么：加入公众持有现金（占存款 20%）
- 考什么：条件切换：存款乘数变成 1/(rr+e+c)，基础货币有一部分流到银行体系外
- 旧方法得数：5,000,000，与新答案差 100.0%

## 15. test_2997　FF　C 换数字

**原题**：You are the manager of a bank that has $15 million of fixed-rate assets, $30 million of rate-sensitive assets, $25 million of fixed-rate liabilities, and $20 million of rate-sensitive liabilities.What will be the change in bank profits if interest rates rise by 5 percentage points? (Unit: dollar)

原答案 500,000；程序复现 500,000（income gap = (RSA - RSL) x change in rate）

**新题**：You are the manager of a bank that has $20 million of fixed-rate assets, $25 million of rate-sensitive assets, $15 million of fixed-rate liabilities, and $30 million of rate-sensitive liabilities.What will be the change in bank profits if interest rates rise by 3 percentage points? (Unit: dollar)

**新答案**：-150,000

- 改了什么：换数字，使利率敏感负债大于利率敏感资产
- 考什么：换数字：缺口由正变负，加息后利润下降，答案为负
- 旧方法得数：500,000，与新答案差 433.33%

## 16. test_171　NM　B 反向求解

**原题**：Cookie Dough Manufacturing has a target debt-equity ratio of 0.80. Its cost of equity is 17 percent, and its cost of debt is 10 percent. The tax rate is 35 percent.What is the company's WACC? (Unit: decimal)

原答案 0.1233；程序复现 0.1233（weights from D/E: D/V = 0.8/1.8）

**新题**：Cookie Dough Manufacturing has a cost of equity of 17 percent and a pretax cost of debt of 10 percent. The tax rate is 35 percent. The company's WACC is 12.33 percent.What target debt-equity ratio is the company using? (Unit: decimal)

**新答案**：0.801

- 改了什么：已知 WACC，反求负债权益比
- 考什么：反向求解：要从 D/E 推权重，再解方程。GT 为 0.801（WACC 只给到两位小数，所以不是正好 0.80）

## 17. test_2281　NM　A 条件切换

**原题**：Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt, and its cost of equity is 16 percent. The firm can borrow at 9 percent. The corporate tax rate is 35 percent.What will the value of the firm be if Old School converts to 50 percent debt? (Unit: dollar)

原答案 57,281.25；程序复现 57,281.25（debt = 50% of the unlevered value (V_L = V_U + T_c D); reading "50% of levered value" gives 59,090.91）

**新题**：Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt, and its cost of equity is 16 percent. The firm can borrow at 9 percent. There are no corporate or personal taxes, and capital markets are perfect.What will the value of the firm be if Old School converts to 50 percent debt? (Unit: dollar)

**新答案**：75,000

- 改了什么：有公司税改成无税
- 考什么：条件切换（陷阱）：无税时 MM 定理第一条成立，杠杆不改变公司价值，答案就是无负债时的价值 75,000。顺带消除了原题"50% 负债"指哪种价值的歧义
- 旧方法得数：57,281.25，与新答案差 23.62%

## 18. test_1856　NM　C 换数字

**原题**：Redan Manufacturing uses 2,500 switch assemblies per week and then reorders another 2,500. The relevant carrying cost per switch assembly is $10, and the fixed order cost is $2,400.What is the economic order quantity (EOQ)? (Unit: assembly)

原答案 7,899.37；程序复现 7,899.3671（52 weeks per year; carrying cost is per unit per year）

**新题**：Redan Manufacturing uses 1,800 switch assemblies per week and then reorders another 1,800. The relevant carrying cost per switch assembly is $6 per year, and the fixed order cost is $1,500. Assume 52 weeks per year.What is the economic order quantity (EOQ)? (Unit: assembly)

**新答案**：6,841.0526

- 改了什么：每周用量、持有成本、订货成本都换了新数值
- 考什么：换数字：污染对照。题干补写了"每年 52 周"和"持有成本按年计"，原题没写
- 旧方法得数：7,899.37，与新答案差 15.47%

## 19. test_1506　NM; SP　B 反向求解

**原题**：Kolby Corp. is comparing two different capital structures, Plan I and Plan II. Plan I would result in 1,500 shares of stock and $20,000 in debt, while Plan II would result in 1,100 shares of stock and $30,000 in debt. The interest rate on the debt is 10 percent. The all-equity plan would result in 2,300 shares of stock outstanding.Ignoring taxes, when will EPS be identical for Plans I and II? (Unit: dollar)

原答案 5,750；程序复现 5,750（EPS_I = (EBIT - 2,000)/1,500, EPS_II = (EBIT - 3,000)/1,100）

**新题**：Kolby Corp. is comparing two different capital structures, Plan I and Plan II. Plan I would result in 1,500 shares of stock and $20,000 in debt, while Plan II would result in 1,100 shares of stock. The interest rate on the debt is 10 percent. Ignore taxes.How much debt would Plan II need for EPS under the two plans to be identical when EBIT is $5,750? (Unit: dollar)

**新答案**：30,000

- 改了什么：已知盈亏平衡 EBIT 5,750，反求 Plan II 的负债额
- 考什么：反向求解：先算出 Plan I 在该 EBIT 下的 EPS，再倒推 Plan II 的利息和负债。最初试的是"加 40% 公司税"：盈亏平衡点不变，忽略税的模型也能答对，题目区分不了，所以放弃

## 20. test_2972　NM; TR　A 条件切换

**原题**：You purchase a bond with a coupon rate of 7.5 percent and a clean price of $865. The next semiannual coupon payment is due in three months.What is the invoice price of the bond? (Unit: dollar)

原答案 883.75；程序复现 883.75（semiannual coupon 37.5; half of the period has elapsed）

**新题**：You purchase a bond with a coupon rate of 7.5 percent, a face value of $1,000 and a clean price of $865. The bond pays its coupon once a year, and the next annual coupon payment is due in three months.What is the invoice price of the bond? (Unit: dollar)

**新答案**：921.25

- 改了什么：半年付息改成一年付息
- 考什么：条件切换：应计利息变成一整年息票的 9/12，而不是半年息票的一半
- 旧方法得数：883.75，与新答案差 4.07%
