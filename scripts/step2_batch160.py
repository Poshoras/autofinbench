"""Batch 2: 20 XFinBench seeds x 8 versions = 160 items.

Versions
  O   original question (control, verbatim)
  E   irrelevant information added (answer unchanged)
  F   long natural-language consultation (answer unchanged)
  D1  missing premise            -> should say it cannot be answered and name what is missing
  D2  contradictory premises     -> should point out the contradiction, no number
  D3  false premise in the stem  -> should reject the premise and give the correct number
  D4  outdated rule stated as current (dated Nov 2026) -> flag it; number under the current rule
  D5  a convention left open     -> must state an assumption; number must match that assumption

Every number is computed by the solvers below; each seed's original XFinBench answer
is reproduced first (within 0.5%). Run: python3 -I scripts/step2_batch160.py
"""
import datetime as dt
import json
import math

SEEDS = {json.loads(l)['id']: json.loads(l) for l in open('step2/seeds_200.jsonl')}
TOL = 0.005


# ---------------- solvers ----------------
def bond_price(c, face, y, years, m=1):
    k, i, n = c * face / m, y / m, round(years * m)
    return k * (1 - (1 + i) ** -n) / i + face * (1 + i) ** -n


def binomial(S, K, r, T, steps, kind, american=False, u=None, d=None, sigma=None):
    t = T / steps
    if u is None:
        u = math.exp(sigma * math.sqrt(t)); d = 1 / u
    p = (math.exp(r * t) - d) / (u - d)
    disc = math.exp(-r * t)
    pay = (lambda s: max(s - K, 0)) if kind == 'call' else (lambda s: max(K - s, 0))
    v = [pay(S * u ** j * d ** (steps - j)) for j in range(steps + 1)]
    for n in range(steps - 1, -1, -1):
        v = [disc * (p * v[j + 1] + (1 - p) * v[j]) for j in range(n + 1)]
        if american:
            v = [max(x, pay(S * u ** j * d ** (n - j))) for j, x in enumerate(v)]
    return v[0]


def fv_factor(i, n):
    return ((1 + i) ** n - 1) / i


def days_30_360(d1, d2):
    D1, D2 = min(d1.day, 30), d2.day
    if D2 == 31 and D1 == 30:
        D2 = 30
    return 360 * (d2.year - d1.year) + 30 * (d2.month - d1.month) + (D2 - D1)


def pv(cfs, r):
    return sum(c / (1 + r) ** t for t, c in enumerate(cfs, start=1))


def wacc2(de, re, rd, t):
    return re / (1 + de) + rd * (1 - t) * de / (1 + de)


def oneday(s):
    return dt.date.fromisoformat(s)


NOW = 'It is November 2026. '
SEED_LIST = []


def seed(**kw):
    SEED_LIST.append(kw)


def num(v, **kw):
    return dict(type='number', value=v, **kw)


# =====================================================================
# 1  test_1091  savings account, daily compounding
f1091 = lambda P=6000, apr=.084, yrs=5: P * (1 + apr / 365) ** (365 * yrs)
seed(id='test_1091', repro=f1091(), params=['6,000', '8.4', 'daily', '5 years'],
  E=dict(q='Corpstein Credit Bank is offering 8.4 percent compounded daily on its savings accounts. Its rival, Second Federal, '
           'advertises 8.1 percent compounded monthly, inflation last year was 3.2 percent, and Corpstein charges a $15 fee to open '
           'a certificate of deposit, which does not apply to savings accounts. Suppose you deposit $6,000 today in a Corpstein '
           'savings account.How much will you have in the account in 5 years? (Unit: dollar)',
         gt=num(f1091()), distractors=[8.1, 3.2, 15]),
  F=dict(q='Hi, I hope you can help me think something through. My grandmother passed away last spring and left me a little money. '
           'After paying for the funeral and a few of her outstanding bills, I ended up with $6,000 that I would like to put somewhere '
           'safe. I am 27, I rent a small apartment with a roommate, and I am planning to go back to school for a nursing degree in '
           'about five years, so I will not need to touch this money until then. I have been comparing banks near my office, and '
           'Corpstein Credit Bank is offering 8.4 percent compounded daily on its savings accounts, which is better than what my '
           'credit union pays. My plan is to deposit the whole $6,000 today and leave it alone until I enroll. If I do that, how much '
           'will I have in the account in 5 years? (Unit: dollar)',
         gt=num(f1091())),
  D1=dict(q='Corpstein Credit Bank compounds interest daily on its savings accounts. Suppose you deposit $6,000 today.How much will '
            'you have in the account in 5 years? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the interest rate on the savings account'), removed='8.4'),
  D2=dict(q='Corpstein Credit Bank is offering 8.4 percent compounded daily on its savings accounts, which it advertises as an '
            'effective annual rate (EAR) of 8.0 percent. Suppose you deposit $6,000 today.How much will you have in the account in '
            '5 years? (Unit: dollar)',
          gt=dict(type='contradiction', issue='8.4% compounded daily is an EAR of about 8.76%; an EAR below the quoted 8.4% is impossible'),
          violated=(1 + .084 / 365) ** 365 - 1 > .08 + 1e-9),
  D3=dict(q='Corpstein Credit Bank is offering 8.4 percent compounded daily on its savings accounts. Since daily compounding at a '
            'given annual rate produces the same balance as annual compounding at that rate, suppose you deposit $6,000 today.How '
            'much will you have in the account in 5 years? (Unit: dollar)',
          gt=dict(type='false_premise', issue='daily compounding gives more than annual compounding at the same quoted rate',
                  value=f1091()), premise_value=6000 * 1.084 ** 5),
  D4=dict(q=NOW + 'Corpstein Credit Bank\'s savings account pays the current 12-month USD LIBOR rate, which the bank quotes at '
            '6.4 percent, plus 2.0 percentage points, compounded daily. Suppose you deposit $6,000 today.How much will you have in '
            'the account in 5 years? (Unit: dollar)',
          gt=dict(type='outdated', issue='USD LIBOR no longer exists (all settings ceased; the last synthetic USD LIBOR was '
                  'published on 30 Sep 2024); the reference rate would now be SOFR-based', value=f1091(),
                  value_under_stated_rule=f1091(), flag_only=True)),
  D5=dict(q='Corpstein Credit Bank is offering an 8.4 percent annual interest rate on its savings accounts. Suppose you deposit '
            '$6,000 today.How much will you have in the account in 5 years? (Unit: dollar)',
          gt=dict(type='assumption', about='compounding frequency', options={
              'annual compounding': 6000 * 1.084 ** 5, 'monthly compounding': 6000 * (1 + .084 / 12) ** 60,
              'daily compounding (365)': f1091(), 'continuous compounding': 6000 * math.exp(.42)})),
)

# =====================================================================
# 2  test_3073  saving for retirement, wait 20 years
r_m = .11 / 12
f3073 = 1e6 / fv_factor(r_m, 240)
seed(id='test_3073', repro=f3073, params=['40 years', '11', 'compounded monthly', '20 years', '1,000,000'],
  E=dict(q='You want to be a millionaire when you retire in 40 years. Assume you can earn an 11 percent annual return from your '
           'savings, and you consider making monthly deposits. Your current salary is $52,000, a friend\'s mutual fund returned '
           '14 percent last year, and your employer\'s retirement plan charges a $35 annual account fee that it pays on your '
           'behalf.How much do you have to save each month to be a millionaire if you wait 20 years before you begin your deposits? '
           '(Unit: dollar)',
         gt=num(f3073, note='same reading as XFinBench: 11% is an APR compounded monthly'), distractors=[52000, 14, 35]),
  F=dict(q='I am 25 and just started my first real job after college. My dad keeps telling me that I should aim to be a '
           'millionaire, meaning $1,000,000 in my account, by the time I retire at 65, which is 40 years from now. Honestly, I want '
           'to enjoy my twenties and thirties: travel, maybe buy a car, help my younger brother with tuition. So my plan is to wait '
           '20 years before I start saving anything, and then make a deposit at the end of every month for the 20 years until I '
           'retire. My financial planner says a diversified portfolio can earn about 11 percent a year, compounded monthly. I know '
           'waiting is not ideal, but I want to see the number. How much would I have to put away each month, once I start in 20 '
           'years, to reach the million at retirement? (Unit: dollar)',
         gt=num(f3073)),
  D1=dict(q='You want to be a millionaire when you retire in 40 years. You consider making monthly deposits, but you wait 20 years '
            'before you begin.How much do you have to save each month to be a millionaire? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the rate of return on the savings'), removed='11'),
  D2=dict(q='You want to be a millionaire when you retire in 40 years. Assume you can earn an 11 percent annual return, compounded '
            'monthly. You wait 20 years before you begin, and then make monthly deposits for 25 years until you retire.How much do '
            'you have to save each month to be a millionaire? (Unit: dollar)',
          gt=dict(type='contradiction', issue='20 years of waiting plus 25 years of deposits is 45 years, but retirement is in 40 years'),
          violated=20 + 25 != 40),
  D3=dict(q='You want to be a millionaire when you retire in 40 years. Assume you can earn an 11 percent annual return, compounded '
            'monthly, and you make monthly deposits. Since waiting 20 years before you start only halves the number of deposits, '
            'the monthly amount you need is about twice what it would be if you started today.How much do you have to save each '
            'month to be a millionaire if you wait 20 years before you begin your deposits? (Unit: dollar)',
          gt=dict(type='false_premise', issue='the required deposit is about 10 times, not 2 times, the start-now amount, because '
                  'the money loses 20 years of compounding', value=f3073),
          premise_value=2 * 1e6 / fv_factor(r_m, 480)),
  D4=dict(q=NOW + 'You want to be a millionaire when you retire in 40 years. Your savings will earn the current 12-month USD LIBOR '
            'rate of 5 percent plus 6 percentage points per year, compounded monthly, and you make monthly deposits.How much do you '
            'have to save each month to be a millionaire if you wait 20 years before you begin your deposits? (Unit: dollar)',
          gt=dict(type='outdated', issue='USD LIBOR no longer exists (ceased; last synthetic setting 30 Sep 2024)', value=f3073,
                  value_under_stated_rule=f3073, flag_only=True)),
  D5=dict(q='You want to be a millionaire when you retire in 40 years. Assume you can earn an 11 percent annual return, compounded '
            'monthly, and that inflation will average 3 percent per year. You wait 20 years before you begin making monthly '
            'deposits.How much do you have to save each month to be a millionaire? (Unit: dollar)',
          gt=dict(type='assumption', about='whether "millionaire" means $1 million in future dollars or in today\'s purchasing power',
                  options={'$1,000,000 nominal': f3073, '$1,000,000 in today\'s dollars (target x 1.03^40)':
                           1e6 * 1.03 ** 40 / fv_factor(r_m, 240)})),
)

# =====================================================================
# 3  test_63  bond price
f63 = bond_price(.10, 1000, .1225, 8)
seed(id='test_63', repro=f63, params=['1,000', '10%', 'once a year', '12.25%', 'eight years'],
  E=dict(q='A 10% coupon bond has a face value of $1000, a 12.25% yield to maturity, and eight years to maturity. The bond was issued '
           'two years ago at par, when market yields were 10%; its current yield is 11.25%; and the issuer\'s common stock trades at '
           '$42.What is the price of the bond? (Unit: dollar)',
         gt=num(f63), distractors=[10, 11.25, 42]),
  F=dict(q='My broker called this morning about a corporate bond he thinks would suit my retirement account. I am not very '
           'experienced with bonds, so I wrote down what he said: it has a face value of $1,000, pays a 10% coupon once a year, and '
           'matures in eight years. He mentioned that the company had a rough couple of years but is stable now, and that the '
           'bond\'s yield to maturity is 12.25%, which is why it looks attractive compared with my CDs. Before I call him back I want '
           'to know whether his quote is reasonable. Based on those numbers, what price should one of these bonds sell for? (Unit: dollar)',
         gt=num(f63)),
  D1=dict(q='A 10% coupon bond has a face value of $1000 and eight years to maturity. Coupons are paid annually.What is the price of '
            'the bond? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the yield to maturity (market discount rate)'), removed='12.25'),
  D2=dict(q='A 10% coupon bond with a face value of $1000 and eight years to maturity trades at a premium to its face value, and its '
            'yield to maturity is 12.25%. Coupons are paid annually.What is the price of the bond? (Unit: dollar)',
          gt=dict(type='contradiction', issue='a bond whose coupon rate (10%) is below its yield (12.25%) must trade at a discount, '
                  'not a premium'), violated=f63 < 1000),
  D3=dict(q='A 10% coupon bond has a face value of $1000, a 12.25% yield to maturity, and eight years to maturity, with annual '
            'coupons. Since its coupon rate is below its yield to maturity, the bond trades at a premium.What is the price of the '
            'bond? (Unit: dollar)',
          gt=dict(type='false_premise', issue='coupon below yield means a discount bond', value=f63), premise_value=None),
  D4=dict(q=NOW + 'A 10% coupon bond has a face value of $1000, eight years to maturity, and annual coupons. Its yield is set at the '
            'current 12-month USD LIBOR rate of 7.25% plus a credit spread of 5.00 percentage points.What is the price of the bond? '
            '(Unit: dollar)',
          gt=dict(type='outdated', issue='USD LIBOR no longer exists; a current spread would be quoted over SOFR or Treasuries',
                  value=f63, value_under_stated_rule=f63, flag_only=True)),
  D5=dict(q='A bond pays a 10% coupon annually, has a 12.25% yield to maturity, and has eight years to maturity.What is the price of '
            'the bond? (Unit: dollar)',
          gt=dict(type='assumption', about='face value (price per $1,000 or per $100 of face value)',
                  options={'per $1,000 face': f63, 'per $100 face': f63 / 10})),
)

# =====================================================================
# 4  test_2545  Spears, Inc.: rising dividends then none
spears = lambda r, divs=(11, 15, 19, 23): pv(divs, r)
seed(id='test_2545', repro=spears(.11), params=['$7', '$4', 'four years', '11 percent'],
  E=dict(q='Spears, Inc., has an odd dividend policy. The company has just paid a dividend of $7 per share and has announced that '
           'it will increase the dividend by $4 per share for each of the next four years, and then never pay another dividend. '
           'Spears earned $9.50 per share last year, the industry\'s average price-earnings ratio is 14, and the stock\'s beta is '
           '1.3. The required return on the company\'s stock is 11 percent.How much will you pay for a share of Spears, Inc. today? '
           '(Unit: dollar)',
         gt=num(spears(.11)), distractors=[9.5, 14, 1.3]),
  F=dict(q='My uncle owns shares in Spears, Inc., a family-run company in his town, and he has offered to sell me some of them. The '
           'company is a bit unusual. It has just paid a dividend of $7 a share, and the founder has announced that the dividend will '
           'go up by $4 a share in each of the next four years. After that, the company will stop paying dividends altogether, '
           'because the founder plans to wind the business down and the remaining assets are expected to be worth nothing. My uncle '
           'is not in a hurry, but I want to make him a fair offer. For a holding like this I would want to earn at least 11 '
           'percent a year. What is the most I should pay per share today? (Unit: dollar)',
         gt=num(spears(.11))),
  D1=dict(q='Spears, Inc., has an odd dividend policy. The company has just paid a dividend of $7 per share and has announced that it '
            'will increase the dividend by $4 per share for each of the next four years, and then never pay another dividend.How '
            'much will you pay for a share of Spears, Inc. today? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the required return (discount rate)'), removed='11 percent'),
  D2=dict(q='Spears, Inc., has just paid a dividend of $7 per share and has announced that it will increase the dividend by $4 per '
            'share for each of the next four years, so that the dividend in year four will be $19. It will then never pay another '
            'dividend. The required return is 11 percent.How much will you pay for a share of Spears, Inc. today? (Unit: dollar)',
          gt=dict(type='contradiction', issue='$7 plus four $4 increases is $23 in year four, not $19'), violated=7 + 4 * 4 != 19),
  D3=dict(q='Spears, Inc., has just paid a dividend of $7 per share and will increase the dividend by $4 per share for each of the '
            'next four years, and then never pay another dividend. The required return is 11 percent. Since the company stops paying '
            'dividends after year four, the price today is simply the sum of the four upcoming dividends.How much will you pay for a '
            'share of Spears, Inc. today? (Unit: dollar)',
          gt=dict(type='false_premise', issue='future dividends must be discounted at the required return', value=spears(.11)),
          premise_value=11 + 15 + 19 + 23),
  D4=dict(q=NOW + 'Spears, Inc., has just paid a dividend of $7 per share and will increase the dividend by $4 per share for each of '
            'the next four years, and then never pay another dividend. Investors require a return equal to the current 12-month USD '
            'LIBOR rate of 5 percent plus an equity premium of 6 percentage points.How much will you pay for a share of Spears, Inc. '
            'today? (Unit: dollar)',
          gt=dict(type='outdated', issue='USD LIBOR no longer exists', value=spears(.11), value_under_stated_rule=spears(.11),
                  flag_only=True)),
  D5=dict(q='Spears, Inc., will pay a dividend of $7 per share this year, then increase it by $4 per share for each of the next four '
            'years, and then never pay another dividend. The required return is 11 percent.How much will you pay for a share of '
            'Spears, Inc. today? (Unit: dollar)',
          gt=dict(type='assumption', about='when the $7 dividend is paid',
                  options={'$7 paid today (cum-dividend), then $11-$23 in years 1-4': 7 + spears(.11),
                           '$7 in one year, then $11-$23 in years 2-5': spears(.11, (7, 11, 15, 19, 23))})),
)

# =====================================================================
# 5  test_2275  accrued interest, corporate bond (30/360)
acc = lambda d1, d2, coupon=7: days_30_360(oneday(d1), oneday(d2)) / 180 * coupon / 2
seed(id='test_2275', repro=acc('2014-07-07', '2014-08-08'), params=['7%', 'January 7', 'July 7', 'July 7, 2014', 'August 8, 2014'],
  E=dict(q='A corporate bond pays a 7% coupon on January 7 and July 7. The bond\'s clean price is 98.50, its yield to maturity is '
           '7.4%, and it matures in 2029. The time frame is between July 7, 2014, and August 8, 2014.How much interest accrues per '
           '$100 of principal for a corporate bond between July 7, 2014, and August 8, 2014? (Unit: dollar)',
         gt=num(acc('2014-07-07', '2014-08-08')), distractors=[98.5, 7.4, 2029]),
  F=dict(q='Last summer my father bought a corporate bond through his bank, and I am helping him check the trade confirmation '
           'because the numbers confuse him. The bond pays a 7% annual coupon in two installments, on January 7 and July 7 each '
           'year. He is a retired machinist and very careful with money, so he wants to understand every line. The part we are stuck '
           'on is the interest that had built up after the July 7, 2014 coupon was paid. How much interest accrues per $100 of '
           'principal on this corporate bond between July 7, 2014, and August 8, 2014? (Unit: dollar)',
         gt=num(acc('2014-07-07', '2014-08-08'))),
  D1=dict(q='A corporate bond pays coupons on January 7 and July 7.How much interest accrues per $100 of principal between July 7, '
            '2014, and August 8, 2014? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the coupon rate'), removed='7%'),
  D2=dict(q='A corporate bond pays a 7% coupon on January 7 and July 7. The period between July 7, 2014, and August 8, 2014, counts as '
            '45 days under the bond\'s day count convention.How much interest accrues per $100 of principal over that period? '
            '(Unit: dollar)',
          gt=dict(type='contradiction', issue='the period is 31 days under 30/360 (32 actual days), not 45'),
          violated=days_30_360(oneday('2014-07-07'), oneday('2014-08-08')) != 45),
  D3=dict(q='A corporate bond pays a 7% coupon on January 7 and July 7. Because U.S. corporate bonds accrue interest on an '
            'actual/actual basis, how much interest accrues per $100 of principal between January 7, 2015, and March 1, 2015? '
            '(Unit: dollar)',
          gt=dict(type='false_premise', issue='U.S. corporate bonds use 30/360; actual/actual is used for Treasuries',
                  value=acc('2015-01-07', '2015-03-01')), premise_value=53 / 181 * 3.5),
  D4=dict(q='It is Monday, August 3, 2026. You buy a U.S. corporate bond that pays a 7% coupon on January 7 and July 7, and the trade '
            'settles on the standard T+2 settlement cycle for U.S. corporate bonds.How much accrued interest per $100 of principal '
            'will you pay at settlement? (Unit: dollar)',
          gt=dict(type='outdated', issue='U.S. corporate bonds settle T+1 since 28 May 2024, so settlement is Tue Aug 4, not Wed Aug 5',
                  value=acc('2026-07-07', '2026-08-04'), value_under_stated_rule=acc('2026-07-07', '2026-08-05'))),
  D5=dict(q='A bond pays a 7% coupon on January 7 and July 7.How much interest accrues per $100 of principal between January 7, '
            '2015, and March 1, 2015? (Unit: dollar)',
          gt=dict(type='assumption', about='day count convention (depends on the type of bond)',
                  options={'30/360 (corporate)': acc('2015-01-07', '2015-03-01'), 'actual/actual (Treasury)': 53 / 181 * 3.5})),
)

# =====================================================================
# 6  test_1102  two-step tree, European put
f1102 = lambda r=.12, u=1.1, d=.9, amer=False: binomial(40, 42, r, .5, 2, 'put', american=amer, u=u, d=d)
seed(id='test_1102', repro=f1102(), params=['$40', '10%', 'three-month', '12%', 'continuous', '$42', 'six-month European put'],
  E=dict(q='A stock price is currently $40. Over each of the next two three-month periods, it is expected to go up by 10% or down by '
           '10%. The risk-free interest rate is 12% per annum with continuous compounding. The stock\'s expected return is 15% per '
           'annum, its historical volatility is 18% per annum, and its next earnings announcement is in five weeks.What is the value '
           'of a six-month European put option with a strike price of $42? (Unit: dollar)',
         gt=num(f1102()), distractors=[15, 18]),
  F=dict(q='I work for a mid-sized tech company and a good part of my savings is in company stock, currently $40 a share. With the '
           'layoffs in our industry I am nervous, so I am thinking about buying protection. My brokerage offers a six-month European '
           'put with a $42 strike. Their pricing tool uses a simple model: over each of the next two three-month periods the stock '
           'either goes up 10% or goes down 10%, and the risk-free rate is 12% a year with continuous compounding. My wife thinks '
           'puts are a waste of money, and I want to show her what the fair price is before we argue about it. Under that model, '
           'what is the put worth? (Unit: dollar)',
         gt=num(f1102())),
  D1=dict(q='A stock price is currently $40. Over each of the next two three-month periods, it is expected to go up by 10% or down by '
            '10%.What is the value of a six-month European put option with a strike price of $42? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the risk-free interest rate'), removed='12%'),
  D2=dict(q='A stock price is currently $40. Over each of the next two three-month periods, it is expected to go up by 2% or down by '
            '10%. The risk-free interest rate is 12% per annum with continuous compounding.What is the value of a six-month European '
            'put option with a strike price of $42? (Unit: dollar)',
          gt=dict(type='contradiction', issue='the up factor 1.02 is below the risk-free growth e^(0.12*0.25)=1.030, so the tree '
                  'admits arbitrage (risk-neutral probability above 1)'), violated=1.02 < math.exp(.03)),
  D3=dict(q='A stock price is currently $40. Over each of the next two three-month periods, it is expected to go up by 10% or down by '
            '10%. The risk-free interest rate is 12% per annum with continuous compounding. Since the stock is equally likely to go up '
            'or down, the probability of an up move used to value the option is 0.5.What is the value of a six-month European put '
            'option with a strike price of $42? (Unit: dollar)',
          gt=dict(type='false_premise', issue='valuation uses the risk-neutral probability (about 0.652), not the real-world 0.5',
                  value=f1102()), premise_value=math.exp(-.06) * (2 * .25 * 2.4 + .25 * 9.6)),
  D4=dict(q=NOW + 'A stock price is currently $40. Over each of the next two three-month periods, it is expected to go up by 10% or '
            'down by 10%. The risk-free rate, taken as the current six-month USD LIBOR rate, is 12% per annum with continuous '
            'compounding.What is the value of a six-month European put option with a strike price of $42? (Unit: dollar)',
          gt=dict(type='outdated', issue='USD LIBOR no longer exists; the risk-free proxy would now be SOFR or Treasury rates',
                  value=f1102(), value_under_stated_rule=f1102(), flag_only=True)),
  D5=dict(q='A stock price is currently $40. Over each of the next two three-month periods, it is expected to go up by 10% or down by '
            '10%. The risk-free interest rate is 12% per annum with continuous compounding.What is the value of a six-month put '
            'option with a strike price of $42? (Unit: dollar)',
          gt=dict(type='assumption', about='exercise style', options={'European': f1102(), 'American': f1102(amer=True)})),
)

# =====================================================================
# 7  test_1716  CRR call
f1716 = lambda S=78, kind='call': binomial(S, 80, .03, 4 / 12, 2, kind, sigma=.30)
seed(id='test_1716', repro=f1716(), params=['$78', '30%', '3%', 'two-month', 'four-month', '$80'],
  E=dict(q='The volatility of a non-dividend-paying stock, whose price is $78, is 30%. The risk-free rate is 3% per annum '
           '(continuously compounded) for all maturities. A two-month time step is used for calculations. The stock\'s expected '
           'return is 9% per annum, analysts\' 12-month price target is $90, and the company has 250 million shares outstanding.What '
           'is the value of a four-month European call option with a strike price of $80 given by a two-step binomial tree? '
           '(Unit: dollar)',
         gt=num(f1716()), distractors=[9, 90, 250]),
  F=dict(q='I have been following a non-dividend-paying stock that trades at $78, and I am considering buying a four-month European '
           'call with an $80 strike because I think a new product launch could push the price up. I am taking an online derivatives '
           'course, and the instructor showed us how to value options with a binomial tree. The stock\'s volatility is about 30% a '
           'year, and the risk-free rate is 3% a year, continuously compounded, for all maturities. If I build a two-step binomial '
           'tree with two-month steps, using the standard up and down factors from the volatility, what value does it give for the '
           'call? (Unit: dollar)',
         gt=num(f1716())),
  D1=dict(q='A non-dividend-paying stock\'s price is $78. The risk-free rate is 3% per annum (continuously compounded) for all '
            'maturities. A two-month time step is used for calculations.What is the value of a four-month European call option with '
            'a strike price of $80 given by a two-step binomial tree? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the volatility (or the up and down factors)'), removed='30%'),
  D2=dict(q='A non-dividend-paying stock\'s price is $78. In each two-month step it moves up by a factor of 1.13 or down by a factor '
            'of 0.88, the risk-free rate is 3% per annum (continuously compounded), and the risk-neutral probability of an up move is '
            '0.70.What is the value of a four-month European call option with a strike price of $80 given by a two-step binomial '
            'tree? (Unit: dollar)',
          gt=dict(type='contradiction', issue='with these factors and rate the risk-neutral probability must be '
                  '(e^(0.005)-0.88)/(1.13-0.88) = 0.50, not 0.70'),
          violated=abs((math.exp(.005) - .88) / (1.13 - .88) - .70) > .01),
  D3=dict(q='The volatility of a non-dividend-paying stock, whose price is $78, is 30%. The risk-free rate is 3% per annum '
            '(continuously compounded). A two-month time step is used. Because the call is out of the money today (the stock price '
            'is below the strike), its value is zero.What is the value of a four-month European call option with a strike price of '
            '$80 given by a two-step binomial tree? (Unit: dollar)',
          gt=dict(type='false_premise', issue='an out-of-the-money option still has time value', value=f1716()), premise_value=0.0),
  D4=dict(q=NOW + 'The volatility of a non-dividend-paying stock, whose price is $78, is 30%. The risk-free rate, taken as the '
            'current 3-month USD LIBOR rate, is 3% per annum (continuously compounded). A two-month time step is used.What is the '
            'value of a four-month European call option with a strike price of $80 given by a two-step binomial tree? (Unit: dollar)',
          gt=dict(type='outdated', issue='USD LIBOR no longer exists', value=f1716(), value_under_stated_rule=f1716(),
                  flag_only=True)),
  D5=dict(q='The volatility of a stock whose price is $78 is 30%. The risk-free rate is 3% per annum (continuously compounded). The '
            'company may pay a dividend of $1.50 per share in three months, but the board has not decided. A two-month time step is '
            'used.What is the value of a four-month European call option with a strike price of $80 given by a two-step binomial '
            'tree? (Unit: dollar)',
          gt=dict(type='assumption', about='whether the $1.50 dividend is paid',
                  options={'no dividend': f1716(),
                           'dividend paid (tree on S minus PV of dividend)': f1716(S=78 - 1.5 * math.exp(-.03 * .25))})),
)

# =====================================================================
# 8  test_1822  one-step tree, call
p1822 = lambda r=.08, up=42, dn=38: (40 * math.exp(r / 12) - dn) / (up - dn)
f1822 = lambda kind='call': math.exp(-.08 / 12) * (p1822() * 3 if kind == 'call' else (1 - p1822()) * 1)
seed(id='test_1822', repro=f1822(), params=['$40', '$42', '$38', '8%', 'continuous', '$39', 'one-month'],
  E=dict(q='A stock price is currently $40. At the end of one month, it will be either $42 or $38. The risk-free interest rate is 8% '
           'per annum with continuous compounding. Analysts estimate a 70% chance that the stock will rise to $42, and the stock\'s '
           'average daily trading volume is 2 million shares.What is the value of a one-month European call option with a strike '
           'price of $39? (Unit: dollar)',
         gt=num(f1822()), distractors=[70, 2]),
  F=dict(q='I trade a little on the side and I am trying to understand how options are priced instead of just guessing. There is a '
           'stock I follow that is at $40 right now. For a simple exercise, assume that one month from now it will be at either $42 '
           'or $38, nothing in between. The risk-free rate is 8% per year with continuous compounding. I want to price a one-month '
           'European call with a $39 strike using no-arbitrage reasoning, the way the textbook does with a replicating portfolio. My '
           'roommate says the answer is just the average payoff, but I do not think that is right. What is the call worth? '
           '(Unit: dollar)',
         gt=num(f1822())),
  D1=dict(q='A stock price is currently $40. At the end of one month, it will be either $42 or $38.What is the value of a one-month '
            'European call option with a strike price of $39? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the risk-free interest rate'), removed='8%'),
  D2=dict(q='A stock price is currently $40. At the end of one month, it will be either $42 or $41. The risk-free interest rate is 8% '
            'per annum with continuous compounding.What is the value of a one-month European call option with a strike price of $39? '
            '(Unit: dollar)',
          gt=dict(type='contradiction', issue='both outcomes beat the risk-free growth of $40 (to about $40.27), so the setup admits '
                  'arbitrage'), violated=41 > 40 * math.exp(.08 / 12)),
  D3=dict(q='A stock price is currently $40. At the end of one month, it will be either $42 or $38. The risk-free interest rate is 8% '
            'per annum with continuous compounding. Since the real-world probability of an up move is 70%, the option\'s value is its '
            'expected payoff of 0.7 x $3, discounted at the risk-free rate.What is the value of a one-month European call option with '
            'a strike price of $39? (Unit: dollar)',
          gt=dict(type='false_premise', issue='no-arbitrage value uses the risk-neutral probability, not the real-world one',
                  value=f1822()), premise_value=.7 * 3 * math.exp(-.08 / 12)),
  D4=dict(q=NOW + 'A stock price is currently $40. At the end of one month, it will be either $42 or $38. The risk-free rate, taken as '
            'the current 1-month USD LIBOR rate, is 8% per annum with continuous compounding.What is the value of a one-month '
            'European call option with a strike price of $39? (Unit: dollar)',
          gt=dict(type='outdated', issue='USD LIBOR no longer exists', value=f1822(), value_under_stated_rule=f1822(),
                  flag_only=True)),
  D5=dict(q='A stock price is currently $40. At the end of one month, it will be either $42 or $38. The risk-free interest rate is 8% '
            'per annum with continuous compounding.What is the value of a one-month European option with a strike price of $39? '
            '(Unit: dollar)',
          gt=dict(type='assumption', about='call or put', options={'call': f1822(), 'put': f1822('put')})),
)

# =====================================================================
# 9  test_1137  lower bound for a call
f1137 = lambda div=0.0: 28 - div * math.exp(-.08 * 2 / 12) - 25 * math.exp(-.08 * 4 / 12)
seed(id='test_1137', repro=f1137(), params=['four-month', '$28', '$25', '8%'],
  E=dict(q='A four-month call option on a non-dividend-paying stock has a stock price of $28, a strike price of $25, and the '
           'risk-free interest rate is 8% per annum. The call currently trades at $4.20, the stock\'s volatility is 35%, and its beta '
           'is 0.9.What is a lower bound for the price of the call option? (Unit: dollar)',
         gt=num(f1137()), distractors=[4.2, 35, .9]),
  F=dict(q='I am studying for a finance exam and also trying to apply it to my own small trading account, so I want to get this '
           'right. There is a four-month call option on a stock that does not pay dividends. The stock is at $28, the strike is $25, '
           'and the risk-free rate is 8% per year with continuous compounding. My study partner says the call can never trade below '
           '$3 because that is what you would get by exercising now, but the textbook talks about a tighter bound that uses the '
           'present value of the strike. What is the lower bound for the price of this call, in the textbook sense? (Unit: dollar)',
         gt=num(f1137())),
  D1=dict(q='A four-month call option on a non-dividend-paying stock has a strike price of $25, and the risk-free interest rate is 8% '
            'per annum.What is the standard no-arbitrage lower bound for the price of the call option? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the current stock price'), removed='$28'),
  D2=dict(q='A four-month call option on a non-dividend-paying stock has a stock price of $28, a strike price of $25, and the '
            'risk-free interest rate is 8% per annum; the call is currently 10% out of the money.What is a lower bound for the price '
            'of the call option? (Unit: dollar)',
          gt=dict(type='contradiction', issue='with the stock at $28 above the $25 strike, the call is in the money, not out of the '
                  'money'), violated=28 > 25),
  D3=dict(q='A four-month call option on a non-dividend-paying stock has a stock price of $28, a strike price of $25, and the '
            'risk-free interest rate is 8% per annum. Because the stock pays no dividends, the lower bound for the call is simply the '
            'stock price minus the strike price.What is the lower bound for the price of the call option? (Unit: dollar)',
          gt=dict(type='false_premise', issue='the bound is S minus the present value of K, which is tighter than S minus K',
                  value=f1137()), premise_value=3.0),
  D4=dict(q=NOW + 'A four-month call option on a non-dividend-paying stock has a stock price of $28 and a strike price of $25. The '
            'risk-free rate, taken as the current 3-month USD LIBOR rate, is 8% per annum.What is a lower bound for the price of the '
            'call option? (Unit: dollar)',
          gt=dict(type='outdated', issue='USD LIBOR no longer exists', value=f1137(), value_under_stated_rule=f1137(),
                  flag_only=True)),
  D5=dict(q='A four-month call option on a stock has a stock price of $28, a strike price of $25, and the risk-free interest rate is '
            '8% per annum with continuous compounding. The company may pay a dividend of $1.00 per share in two months; the board '
            'has not yet decided.What is a lower bound for the price of the call option? (Unit: dollar)',
          gt=dict(type='assumption', about='whether the dividend is paid',
                  options={'no dividend': f1137(), '$1.00 dividend paid': f1137(1.0)})),
)

# =====================================================================
# 10  test_1907  index futures price
f1907 = lambda r=.10, q=.04, T=4 / 12: 400 * math.exp((r - q) * T)
seed(id='test_1907', repro=f1907(), params=['10%', 'continuous', '4%', '400', 'four months'],
  E=dict(q='Suppose that the risk-free interest rate is 10% per annum with continuous compounding and that the dividend yield on a '
           'stock index is 4% per annum. The index is standing at 400, and the futures price for a contract deliverable in four '
           'months is 405. The index\'s volatility is 18%, it rose 12% over the past year, and a six-month contract trades at 413.What '
           'is the theoretical futures price for a contract deliverable in four months? (Unit: dollar)',
         gt=num(f1907()), distractors=[405, 18, 12, 413]),
  F=dict(q='I manage the investments of a small family office, and we use stock index futures to adjust our equity exposure. Before '
           'we roll our position I want to check whether the futures are fairly priced. The index is at 400 today. The risk-free '
           'rate is 10% a year with continuous compounding, and the index has a dividend yield of 4% a year, also continuous. Our '
           'broker\'s screen is down, so I cannot see the quoted futures price right now, and I just want the theoretical value '
           'from cost of carry. What should the futures price be for a contract deliverable in four months? (Unit: dollar)',
         gt=num(f1907())),
  D1=dict(q='Suppose that the dividend yield on a stock index is 4% per annum. The index is standing at 400.What is the theoretical '
            'futures price for a contract deliverable in four months? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the risk-free interest rate'), removed='10%'),
  D2=dict(q='Suppose that the risk-free interest rate is 10% per annum with continuous compounding and that the dividend yield on a '
            'stock index is 4% per annum. The index is standing at 400 and its constituents pay dividends totaling 25 index points '
            'per year.What is the theoretical futures price for a contract deliverable in four months? (Unit: dollar)',
          gt=dict(type='contradiction', issue='25 points a year on an index of 400 is a 6.25% yield, not 4%'),
          violated=abs(25 / 400 - .04) > .001),
  D3=dict(q='Suppose that the risk-free interest rate is 10% per annum with continuous compounding and that the dividend yield on a '
            'stock index is 4% per annum. The index is standing at 400. Since dividends on the index raise the futures price above '
            'what it would be without dividends, what is the theoretical futures price for a contract deliverable in four months? '
            '(Unit: dollar)',
          gt=dict(type='false_premise', issue='dividends lower the futures price (F = S e^{(r-q)T})', value=f1907()),
          premise_value=400 * math.exp((.10 + .04) * 4 / 12)),
  D4=dict(q=NOW + 'The risk-free interest rate, taken as the current 4-month USD LIBOR rate, is 10% per annum with continuous '
            'compounding, and the dividend yield on a stock index is 4% per annum. The index is standing at 400.What is the '
            'theoretical futures price for a contract deliverable in four months? (Unit: dollar)',
          gt=dict(type='outdated', issue='USD LIBOR no longer exists (and there was never a 4-month tenor)', value=f1907(),
                  value_under_stated_rule=f1907(), flag_only=True)),
  D5=dict(q='Suppose that the risk-free interest rate is 10% per annum and the dividend yield on a stock index is 4% per annum. The '
            'index is standing at 400.What is the theoretical forward price for a contract deliverable in three years? (Unit: dollar)',
          gt=dict(type='assumption', about='compounding convention of the quoted rates',
                  options={'continuous compounding': f1907(T=3), 'annual compounding': 400 * (1.10 / 1.04) ** 3})),
)

# =====================================================================
# 11  test_674  initial investment with an opportunity cost
f674 = lambda land=5.3e6: land + 11.6e6 + .425e6
seed(id='test_674', repro=f674(), params=['$5 million', '$5.3 million', '$11.6 million', '425,000'],
  E=dict(q='Parker & Stone, Inc., is looking at setting up a new manufacturing plant in South Park to produce garden tools. The company '
           'bought some land six years ago for $5 million in anticipation of using it as a warehouse and distribution site, but the '
           'company has since decided to rent these facilities from a competitor instead. If the land were sold today, the company '
           'would net $5.3 million. The new plant will cost $11.6 million to build, and the site requires $425,000 worth of grading '
           'before it is suitable for construction. Last year the company spent $250,000 on a feasibility study for the plant, its '
           'WACC is 11 percent, and the plant will be depreciated over 20 years.What is the proper cash flow amount to use as the '
           'initial investment in fixed assets when evaluating this project? (Unit: dollar)',
         gt=num(f674()), distractors=[250000, 11, 20]),
  F=dict(q='I am the controller at Parker & Stone, a family-owned maker of garden tools, and the owners asked me to put together the '
           'numbers for a new plant in South Park. Some background: six years ago we bought a plot of land for $5 million because we '
           'planned to build a warehouse and distribution center there. We later decided to rent warehouse space from a competitor '
           'instead, so the land has been sitting empty. A broker tells me that if we sold it today we would net $5.3 million. Now '
           'the idea is to build the plant on that land. The construction quote is $11.6 million, and the site needs $425,000 of '
           'grading before construction can start. What cash flow should I use as the initial investment in fixed assets when '
           'evaluating the plant? (Unit: dollar)',
         gt=num(f674())),
  D1=dict(q='Parker & Stone, Inc., is looking at setting up a new manufacturing plant in South Park to produce garden tools. The company '
            'bought some land six years ago for $5 million in anticipation of using it as a warehouse and distribution site, but the '
            'company has since decided to rent these facilities from a competitor instead. The new plant will be built on this land; '
            'it will cost $11.6 million to build, and the site requires $425,000 worth of grading.What is the proper cash flow amount '
            'to use as the initial investment in fixed assets when evaluating this project? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='what the land could be sold for today (its opportunity cost); the $5 million paid '
                  'is sunk'), removed='5.3'),
  D2=dict(q='Parker & Stone, Inc., bought some land six years ago for $5 million. If the land were sold today, the company would net '
            '$5.3 million, a loss of $700,000 relative to what it paid. The company plans to build a new plant on the land instead; '
            'the plant will cost $11.6 million, and the site requires $425,000 worth of grading.What is the proper cash flow amount '
            'to use as the initial investment in fixed assets when evaluating this project? (Unit: dollar)',
          gt=dict(type='contradiction', issue='selling for $5.3 million after paying $5 million is a $300,000 gain, not a $700,000 '
                  'loss'), violated=5.3e6 - 5e6 != -7e5),
  D3=dict(q='Parker & Stone, Inc., bought some land six years ago for $5 million; if sold today, it would net $5.3 million. The company '
            'plans to build a new plant on the land; the plant will cost $11.6 million, and the site requires $425,000 worth of '
            'grading. Since the land was bought six years ago, its cost is sunk and the land should be left out of the initial '
            'investment.What is the proper cash flow amount to use as the initial investment in fixed assets when evaluating this '
            'project? (Unit: dollar)',
          gt=dict(type='false_premise', issue='the historical cost is sunk, but the land\'s current value is an opportunity cost '
                  'and must be included', value=f674()), premise_value=f674(0)),
  D4=dict(q=NOW + 'Parker & Stone, Inc., bought some land six years ago for $5 million. If the land were sold today, the company would '
            'receive $5.3 million before taxes. The $300,000 gain would be taxed at the current U.S. federal corporate income tax '
            'rate of 35 percent; ignore state taxes.How much federal tax would the sale of the land generate? (Unit: dollar)',
          gt=dict(type='outdated', issue='the federal corporate rate has been a flat 21% since 2018 (TCJA), not 35%',
                  value=.21 * 3e5, value_under_stated_rule=.35 * 3e5)),
  D5=dict(q='Parker & Stone, Inc., bought some land six years ago for $5 million. Brokers estimate the land would sell today for '
            'between $5.0 million and $5.6 million, net of selling costs. The company plans to build a new plant on the land instead; '
            'the plant will cost $11.6 million, and the site requires $425,000 worth of grading.What is the proper cash flow amount to '
            'use as the initial investment in fixed assets when evaluating this project? (Unit: dollar)',
          gt=dict(type='assumption', about='which land value in the $5.0-5.6 million range to use; the answer must equal '
                  '$12,025,000 plus the stated land value',
                  options={'land at $5.0M': f674(5.0e6), 'land at $5.3M (midpoint)': f674(5.3e6), 'land at $5.6M': f674(5.6e6)})),
)

# =====================================================================
# 12  test_945  deposit expansion with excess reserves
seed(id='test_945', repro=1e6 / (.10 + .10), params=['$1 million', '10%', 'excess reserves'],
  E=dict(q='If the Fed buys $1 million of bonds from the First National Bank, and an additional 10% of any deposit is held as excess '
           'reserves, the reserve requirement ratio is 10%. The federal funds rate is 4.25%, the First National Bank has $250 million '
           'in total assets, and the discount rate is 4.75%.What is the total increase in checkable deposits? (Unit: dollar)',
         gt=num(1e6 / .2), distractors=[4.25, 250, 4.75]),
  F=dict(q='I am writing an explainer for our college newspaper about how the Fed creates money, and I want to use a concrete example '
           'that I can check. Suppose the Fed buys $1 million of bonds from the First National Bank. Banks are required to hold 10% '
           'of their checkable deposits as reserves, and in my example they also choose to keep an extra 10% of any new deposit as '
           'excess reserves because they are being cautious. Assume nobody changes how much cash they hold. After the money works its '
           'way through the whole banking system, how much will checkable deposits have increased in total? (Unit: dollar)',
         gt=num(1e6 / .2)),
  D1=dict(q='If the Fed buys bonds from the First National Bank, and an additional 10% of any deposit is held as excess reserves, the '
            'reserve requirement ratio is 10%.What is the total increase in checkable deposits? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the amount of the Fed\'s bond purchase'), removed='$1 million'),
  D2=dict(q='The Fed buys $1 million of bonds from the First National Bank. The reserve requirement ratio is 10%, and banks hold an '
            'additional 10% of any deposit as excess reserves, so banks keep total reserves equal to 15% of their deposits.What is the '
            'total increase in checkable deposits? (Unit: dollar)',
          gt=dict(type='contradiction', issue='10% required plus 10% excess is 20% of deposits, not 15%'), violated=.10 + .10 != .15),
  D3=dict(q='The Fed buys $1 million of bonds from the First National Bank. The reserve requirement ratio is 10%, and banks hold an '
            'additional 10% of any deposit as excess reserves. Because banks hold excess reserves, the deposit multiplier is larger '
            'than it would be without them.What is the total increase in checkable deposits? (Unit: dollar)',
          gt=dict(type='false_premise', issue='excess reserves reduce the multiplier (1/(rr+e) = 5 instead of 10)', value=1e6 / .2),
          premise_value=None),
  D4=dict(q=NOW + 'The Fed buys $1 million of bonds from the First National Bank. Under the Federal Reserve\'s current required '
            'reserve ratio of 10% on checkable deposits, and with banks holding an additional 10% of any deposit as excess reserves, '
            'what is the total increase in checkable deposits? (Unit: dollar)',
          gt=dict(type='outdated', issue='Fed reserve requirement ratios have been 0% since 26 March 2020',
                  value=1e6 / (0 + .10), value_under_stated_rule=1e6 / .2)),
  D5=dict(q='The Fed buys $1 million of bonds from the First National Bank. The reserve requirement ratio is 10%, and banks hold an '
            'additional 10% of any deposit as excess reserves. Some of the new deposits may be withdrawn by the public as cash.What is '
            'the total increase in checkable deposits? (Unit: dollar)',
          gt=dict(type='assumption', about='currency drain c (cash held per dollar of deposits); answer must equal 1,000,000/(0.20+c) '
                  'for the stated c', options={'no currency drain (c = 0)': 1e6 / .2, 'example c = 0.20': 1e6 / .4})),
)

# =====================================================================
# 13  test_2758  depositing $100 of cash
seed(id='test_2758', repro=100 / .05, params=['$100', '5%', 'currency holdings constant'],
  E=dict(q='You decide to hold $100 less cash than usual and deposit $100 in cash in the bank. The rest of the public keeps its '
           'holdings of currency constant. Your checking account pays 0.5% interest, your bank has 12 branches, and the Fed pays '
           '4.4% interest on reserve balances.If the reserve ratio (rr) is 5%, by how much will checkable deposits rise? (Unit: dollar)',
         gt=num(2000), distractors=[.5, 12, 4.4]),
  F=dict(q='I usually keep a few hundred dollars in cash at home, partly out of habit from my parents. This month I decided to keep '
           '$100 less cash than usual and deposit that $100 into my checking account. In my economics class we are studying how '
           'deposits get multiplied through the banking system, and I want to apply it to my own little deposit. Assume that nobody '
           'else changes how much cash they hold (the rest of the public keeps its currency holdings constant), banks keep 5% of '
           'checkable deposits as reserves, and they lend out everything else. By how much will checkable deposits in the banking '
           'system rise in the end? (Unit: dollar)',
         gt=num(2000)),
  D1=dict(q='You decide to hold $100 less cash than usual and deposit $100 in cash in the bank. The rest of the public keeps its '
            'holdings of currency constant.By how much will checkable deposits rise? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the reserve ratio'), removed='5%'),
  D2=dict(q='You decide to hold $100 less cash than usual and deposit $100 in cash in the bank. The rest of the public keeps its '
            'holdings of currency constant. The reserve ratio is 5%, so for each $100 of deposits the bank must hold $10 in reserves.'
            'By how much will checkable deposits rise? (Unit: dollar)',
          gt=dict(type='contradiction', issue='5% of $100 is $5, not $10'), violated=.05 * 100 != 10),
  D3=dict(q='You decide to hold $100 less cash than usual and deposit $100 in cash in the bank. The rest of the public keeps its '
            'holdings of currency constant, and the reserve ratio is 5%. Since you only moved $100 from your pocket into the bank, '
            'checkable deposits in the banking system cannot rise by more than $100.By how much will checkable deposits rise? '
            '(Unit: dollar)',
          gt=dict(type='false_premise', issue='the new reserves support multiple deposit creation (1/0.05 = 20 times)', value=2000),
          premise_value=100),
  D4=dict(q=NOW + 'You decide to hold $100 less cash than usual and deposit $100 in cash in the bank. The rest of the public keeps its '
            'holdings of currency constant. Banks hold excess reserves equal to 2% of deposits, in addition to the Federal Reserve\'s '
            'current required reserve ratio of 5% on checkable deposits.By how much will checkable deposits rise? (Unit: dollar)',
          gt=dict(type='outdated', issue='Fed reserve requirement ratios have been 0% since 26 March 2020',
                  value=100 / .02, value_under_stated_rule=100 / .07)),
  D5=dict(q='You decide to hold $100 less cash than usual and deposit $100 in cash in the bank. The rest of the public keeps its '
            'holdings of currency constant, and the required reserve ratio is 5%. Banks may also hold some excess reserves.By how '
            'much will checkable deposits rise? (Unit: dollar)',
          gt=dict(type='assumption', about='excess reserve ratio e; answer must equal 100/(0.05+e) for the stated e',
                  options={'no excess reserves (e = 0)': 2000, 'example e = 0.05': 1000})),
)

# =====================================================================
# 14  test_171  WACC from a D/E ratio
seed(id='test_171', repro=wacc2(.8, .17, .10, .35), params=['0.80', '17', '10', '35'],
  E=dict(q='Cookie Dough Manufacturing has a target debt-equity ratio of 0.80. Its cost of equity is 17 percent, and its cost of debt '
           'is 10 percent. The tax rate is 35 percent. The company\'s stock beta is 1.25, the market risk premium is 7 percent, its '
           'bonds carry an 8 percent coupon, and it has 2 million shares outstanding.What is the company\'s WACC? (Unit: decimal)',
         gt=num(wacc2(.8, .17, .10, .35)), distractors=[1.25, 7, 8, 2]),
  F=dict(q='I just joined Cookie Dough Manufacturing as a junior analyst, and my first assignment is to update the discount rate we '
           'use for new oven lines. My manager is on vacation, so I am piecing things together from old files. Our CFO targets a '
           'debt-to-equity ratio of 0.80. Our cost of equity is 17 percent, and our pre-tax cost of debt is 10 percent. The tax rate '
           'we use in planning is 35 percent. I want to make sure I weight things correctly, because last year\'s file seems to have '
           'used the debt-to-equity ratio directly as the debt weight. What WACC should I use? (Unit: decimal)',
         gt=num(wacc2(.8, .17, .10, .35))),
  D1=dict(q='Cookie Dough Manufacturing\'s cost of equity is 17 percent, and its cost of debt is 10 percent. The tax rate is 35 '
            'percent.What is the company\'s WACC? (Unit: decimal)',
          gt=dict(type='cannot_answer', missing='the capital structure weights (target debt-equity ratio)'), removed='0.80'),
  D2=dict(q='Cookie Dough Manufacturing has a target debt-equity ratio of 0.80, meaning that debt makes up 80 percent of its total '
            'capital. Its cost of equity is 17 percent, and its cost of debt is 10 percent. The tax rate is 35 percent.What is the '
            'company\'s WACC? (Unit: decimal)',
          gt=dict(type='contradiction', issue='a D/E of 0.80 means debt is 0.8/1.8 = 44.4% of capital, not 80%'),
          violated=abs(.8 / 1.8 - .8) > .01),
  D3=dict(q='Cookie Dough Manufacturing has a target debt-equity ratio of 0.80. Its cost of equity is 17 percent, and its cost of debt '
            'is 10 percent. The tax rate is 35 percent. Since both interest and dividends are tax-deductible, both the cost of debt '
            'and the cost of equity should be adjusted for taxes.What is the company\'s WACC? (Unit: decimal)',
          gt=dict(type='false_premise', issue='dividends are not tax-deductible; only the cost of debt is tax-adjusted',
                  value=wacc2(.8, .17, .10, .35)), premise_value=wacc2(.8, .17 * .65, .10, .35)),
  D4=dict(q=NOW + 'Cookie Dough Manufacturing has a target debt-equity ratio of 0.80. Its cost of equity is 17 percent, and its '
            'pre-tax cost of debt is 10 percent. The company pays the current U.S. federal statutory corporate income tax rate of 35 '
            'percent; ignore state taxes.What is the company\'s WACC? (Unit: decimal)',
          gt=dict(type='outdated', issue='the federal corporate rate has been a flat 21% since 2018 (TCJA), not 35%',
                  value=wacc2(.8, .17, .10, .21), value_under_stated_rule=wacc2(.8, .17, .10, .35))),
  D5=dict(q='Cookie Dough Manufacturing has a target debt-equity ratio of 0.80. Its cost of equity is 17 percent. The financing desk '
            'reports a cost of debt of 10 percent but does not say whether this is before or after taxes. The tax rate is 35 '
            'percent.What is the company\'s WACC? (Unit: decimal)',
          gt=dict(type='assumption', about='whether the 10% cost of debt is pre-tax or after-tax',
                  options={'10% is pre-tax': wacc2(.8, .17, .10, .35), '10% is already after-tax': wacc2(.8, .17, .10, 0)})),
)

# =====================================================================
# 15  test_701  WACC with preferred stock
w701 = lambda t=.35, we=.50, wp=.05, wd=.45, pref_tax=False: we * .15 + wp * .06 * ((1 - t) if pref_tax else 1) + wd * .08 * (1 - t)
seed(id='test_701', repro=w701(), params=['50 percent', '5 percent', '45 percent', '15 percent', '6 percent', '8 percent', '35 percent'],
  E=dict(q='Mullineaux Corporation has a target capital structure of 50 percent common stock, 5 percent preferred stock, and 45 '
           'percent debt. Its cost of equity is 15 percent, the cost of preferred stock is 6 percent, and the cost of debt is 8 '
           'percent. The relevant tax rate is 35 percent. Its common stock trades at $45 with a beta of 1.2, its preferred pays a $6 '
           'dividend, and the company was founded in 1962.What is Mullineaux\'s WACC? (Unit: decimal)',
         gt=num(w701()), distractors=[45, 1.2, 6, 1962]),
  F=dict(q='My sister is doing an MBA and asked me to double-check a case she is working on, since I work in corporate finance. The '
           'case company is Mullineaux Corporation. Its target capital structure is 50 percent common stock, 5 percent preferred '
           'stock, and 45 percent debt. The case gives a cost of equity of 15 percent, a cost of preferred stock of 6 percent, and a '
           'pre-tax cost of debt of 8 percent, with a tax rate of 35 percent. She got a number that looks too low to her, and she is '
           'not sure whether the preferred stock should get a tax adjustment like the debt does. What is Mullineaux\'s WACC? '
           '(Unit: decimal)',
         gt=num(w701())),
  D1=dict(q='Mullineaux Corporation has a target capital structure of 50 percent common stock, 5 percent preferred stock, and 45 '
            'percent debt. Its cost of equity is 15 percent, the cost of preferred stock is 6 percent, and the pre-tax cost of debt is '
            '8 percent.What is Mullineaux\'s WACC? (Unit: decimal)',
          gt=dict(type='cannot_answer', missing='the tax rate (needed for the after-tax cost of debt)'), removed='35 percent'),
  D2=dict(q='Mullineaux Corporation has a target capital structure of 50 percent common stock, 5 percent preferred stock, and 55 '
            'percent debt. Its cost of equity is 15 percent, the cost of preferred stock is 6 percent, and the cost of debt is 8 '
            'percent. The relevant tax rate is 35 percent.What is Mullineaux\'s WACC? (Unit: decimal)',
          gt=dict(type='contradiction', issue='the weights add up to 110%'), violated=.50 + .05 + .55 != 1),
  D3=dict(q='Mullineaux Corporation has a target capital structure of 50 percent common stock, 5 percent preferred stock, and 45 '
            'percent debt. Its cost of equity is 15 percent, the cost of preferred stock is 6 percent, and the cost of debt is 8 '
            'percent. The relevant tax rate is 35 percent. Since preferred dividends are tax-deductible like interest, the cost of '
            'preferred stock should also be adjusted for taxes.What is Mullineaux\'s WACC? (Unit: decimal)',
          gt=dict(type='false_premise', issue='preferred dividends are not tax-deductible', value=w701()),
          premise_value=w701(pref_tax=True)),
  D4=dict(q=NOW + 'Mullineaux Corporation has a target capital structure of 50 percent common stock, 5 percent preferred stock, and 45 '
            'percent debt. Its cost of equity is 15 percent, the cost of preferred stock is 6 percent, and the pre-tax cost of debt is '
            '8 percent. The company pays the current U.S. federal statutory corporate income tax rate of 35 percent; ignore state '
            'taxes.What is Mullineaux\'s WACC? (Unit: decimal)',
          gt=dict(type='outdated', issue='the federal corporate rate has been a flat 21% since 2018 (TCJA), not 35%',
                  value=w701(.21), value_under_stated_rule=w701(.35))),
  D5=dict(q='Mullineaux Corporation has a target capital structure of 50 percent common stock, 5 percent preferred stock, and 45 '
            'percent debt. Its cost of equity is 15 percent, the cost of preferred stock is 6 percent, and the pre-tax cost of debt is '
            '8 percent. Its marginal tax rate is either the 21 percent federal rate alone or about 25 percent including state taxes; '
            'the case materials do not say which applies.What is Mullineaux\'s WACC? (Unit: decimal)',
          gt=dict(type='assumption', about='which tax rate applies', options={'21% (federal only)': w701(.21),
                                                                             '25% (federal and state)': w701(.25)})),
)

# =====================================================================
# 16  test_2281  M&M with corporate taxes
vu = lambda t=.35: 12000 * (1 - t) / .16
seed(id='test_2281', repro=vu() + .35 * .5 * vu(), params=['12,000', '16 percent', '9 percent', '35 percent', 'half'],
  E=dict(q='Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt, and its cost of '
           'equity is 16 percent. The firm can borrow at 9 percent. The corporate tax rate is 35 percent. The firm has 10,000 shares '
           'outstanding, its EBIT last year was $11,200, and the industry average debt ratio is 40 percent.What will the value of the '
           'firm be if Old School borrows an amount equal to 50 percent of its current all-equity value and uses it to repurchase '
           'shares? (Unit: dollar)',
         gt=num(vu() + .35 * .5 * vu(), note='debt = 50% of the unlevered value, as in the XFinBench answer'),
         distractors=[10000, 11200, 40]),
  F=dict(q='My family owns Old School Corporation, a small business that has been very steady. It earns $12,000 in EBIT every year, '
           'and we expect that to continue forever. We have never borrowed. Investors in a business like ours would require 16 '
           'percent on the equity, and our bank says we can borrow at 9 percent. We pay corporate tax at 35 percent. The banker '
           'suggests we borrow an amount equal to half of what the company is worth today as an all-equity firm, use it to buy back '
           'some of my cousins\' shares, and keep that debt in place permanently. My aunt thinks borrowing can only make the company '
           'worth less. If we follow the banker\'s plan, what would the company be worth? (Unit: dollar)',
         gt=num(vu() + .35 * .5 * vu())),
  D1=dict(q='Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt. The firm can borrow '
            'at 9 percent. The corporate tax rate is 35 percent.What will the value of the firm be if Old School borrows an amount '
            'equal to 50 percent of its current all-equity value? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the unlevered cost of equity (needed to value the all-equity firm)'),
          removed='16 percent'),
  D2=dict(q='Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt, its cost of equity '
            'is 16 percent, and its current all-equity value is $60,000. The firm can borrow at 9 percent. The corporate tax rate is '
            '35 percent.What will the value of the firm be if Old School borrows an amount equal to 50 percent of its current '
            'all-equity value? (Unit: dollar)',
          gt=dict(type='contradiction', issue='12,000 x 0.65 / 0.16 = 48,750, not 60,000'), violated=abs(vu() - 60000) > 1),
  D3=dict(q='Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt, and its cost of '
            'equity is 16 percent. The firm can borrow at 9 percent. The corporate tax rate is 35 percent. Since interest tax shields '
            'have no value when debt is permanent, what will the value of the firm be if Old School borrows an amount equal to 50 '
            'percent of its current all-equity value? (Unit: dollar)',
          gt=dict(type='false_premise', issue='with corporate taxes, permanent debt adds T_c x D to firm value', value=vu() + .35 * .5 * vu()),
          premise_value=vu()),
  D4=dict(q=NOW + 'Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt, and its cost '
            'of equity is 16 percent. The firm can borrow at 9 percent. It pays the current U.S. federal statutory corporate income tax '
            'rate of 35 percent; ignore state taxes.What will the value of the firm be if Old School borrows an amount equal to 50 '
            'percent of its current all-equity value? (Unit: dollar)',
          gt=dict(type='outdated', issue='the federal corporate rate has been a flat 21% since 2018 (TCJA), not 35%',
                  value=vu(.21) + .21 * .5 * vu(.21), value_under_stated_rule=vu() + .35 * .5 * vu())),
  D5=dict(q='Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt, and its cost of '
            'equity is 16 percent. The firm can borrow at 9 percent. The corporate tax rate is 35 percent. Old School plans to borrow '
            'so that debt is 50 percent of the firm\'s value.What will the value of the firm be? (Unit: dollar)',
          gt=dict(type='assumption', about='50% of the current all-equity value or of the post-borrowing (levered) value',
                  options={'50% of all-equity value': vu() + .35 * .5 * vu(), '50% of levered value': vu() / (1 - .5 * .35)})),
)

# =====================================================================
# 17  test_2193  M&M Proposition II with taxes
re2 = lambda t=.35, rebalance=False: .1541 + (.1541 - .08) * 1.0 * (1 if rebalance else (1 - t))
seed(id='test_2193', repro=re2(), params=['35 percent', '15.41 percent', '8 percent', '1.0'],
  E=dict(q='Maxwell Industries has a corporate tax rate of 35 percent. Its unlevered cost of equity capital is 15.41 percent, and its '
           'cost of debt is 8 percent. Maxwell\'s beta is 1.3, it has 5 million shares outstanding, and its existing bonds carry a 7 '
           'percent coupon.What would the cost of equity be if the debt-equity ratio were 1.0? (Unit: decimal)',
         gt=num(re2()), distractors=[1.3, 5, 7]),
  F=dict(q='I sit on the board of Maxwell Industries, and next week we are voting on a recapitalization. Management wants to issue '
           'permanent debt and buy back shares until the debt-equity ratio is 1.0. Several board members are worried that '
           'shareholders will demand a much higher return afterward. Here is what I have from the CFO\'s memo: our corporate tax '
           'rate is 35 percent, our unlevered cost of equity is 15.41 percent, and our cost of debt is 8 percent. I would like to '
           'walk into the meeting knowing the textbook answer. What would our cost of equity be at a debt-equity ratio of 1.0? '
           '(Unit: decimal)',
         gt=num(re2())),
  D1=dict(q='Maxwell Industries has a corporate tax rate of 35 percent, and its cost of debt is 8 percent.What would the cost of equity '
            'be if the debt-equity ratio were 1.0? (Unit: decimal)',
          gt=dict(type='cannot_answer', missing='the unlevered cost of equity (or of assets)'), removed='15.41'),
  D2=dict(q='Maxwell Industries has a corporate tax rate of 35 percent. Its unlevered cost of equity capital is 15.41 percent, and its '
            'cost of debt is 8 percent.What would the cost of equity be if the debt-equity ratio were 1.0, so that debt makes up 75 '
            'percent of the firm\'s value? (Unit: decimal)',
          gt=dict(type='contradiction', issue='a debt-equity ratio of 1.0 means debt is 50% of firm value, not 75%'),
          violated=abs(1 / 2 - .75) > .01),
  D3=dict(q='Maxwell Industries has a corporate tax rate of 35 percent. Its unlevered cost of equity capital is 15.41 percent, and its '
            'cost of debt is 8 percent. Since the interest tax shield offsets the extra risk, M&M Proposition II with taxes says the '
            'cost of equity does not change with leverage.What would the cost of equity be if the debt-equity ratio were 1.0? '
            '(Unit: decimal)',
          gt=dict(type='false_premise', issue='Proposition II with taxes: R_E = R_U + (R_U - R_D)(D/E)(1 - T_C), so R_E rises',
                  value=re2()), premise_value=.1541),
  D4=dict(q=NOW + 'Maxwell Industries pays the current U.S. federal statutory corporate income tax rate of 35 percent; ignore state '
            'taxes. Its unlevered cost of equity capital is 15.41 percent, and its cost of debt is 8 percent.What would the cost of '
            'equity be if the debt-equity ratio were 1.0, with the debt kept permanently? (Unit: decimal)',
          gt=dict(type='outdated', issue='the federal corporate rate has been a flat 21% since 2018 (TCJA), not 35%',
                  value=re2(.21), value_under_stated_rule=re2(.35))),
  D5=dict(q='Maxwell Industries has a corporate tax rate of 35 percent. Its unlevered cost of equity capital is 15.41 percent, and its '
            'cost of debt is 8 percent. The company has not decided whether it will keep the dollar amount of debt fixed or rebalance '
            'its debt to keep the ratio constant.What would the cost of equity be if the debt-equity ratio were 1.0? (Unit: decimal)',
          gt=dict(type='assumption', about='debt policy',
                  options={'fixed (permanent) debt: R_U + (R_U - R_D)(D/E)(1 - T)': re2(),
                           'debt rebalanced to a constant ratio: R_U + (R_U - R_D)(D/E)': re2(rebalance=True)})),
)

# =====================================================================
# 18  test_1506  EPS indifference between two levered plans
be = lambda r1=.10, r2=.10: (1100 * 20000 * r1 - 1500 * 30000 * r2) / (1100 - 1500)
seed(id='test_1506', repro=be(), params=['1,500', '20,000', '1,100', '30,000', '10 percent'],
  E=dict(q='Kolby Corp. is comparing two different capital structures, Plan I and Plan II. Plan I would result in 1,500 shares of '
           'stock and $20,000 in debt, while Plan II would result in 1,100 shares of stock and $30,000 in debt. The interest rate on '
           'the debt is 10 percent. Kolby\'s stock price is $25, last year\'s EBIT was $6,400, and the firm\'s credit rating is BBB.'
           'Ignoring taxes, when will EPS be identical for Plans I and II? (Unit: dollar)',
         gt=num(be()), distractors=[25, 6400]),
  F=dict(q='I run Kolby Corp., a small manufacturing company, and our accountant has given me two ways to restructure our financing. '
           'Under Plan I we would have 1,500 shares outstanding and $20,000 of debt. Under Plan II we would have 1,100 shares '
           'outstanding and $30,000 of debt. Either way the bank charges 10 percent interest. We are a pass-through for now, so please '
           'ignore taxes. Our EBIT bounces around a lot from year to year depending on a couple of big customers, so I want to know '
           'the level of EBIT at which it would not matter to shareholders which plan we picked. At what EBIT would EPS be the same '
           'under both plans? (Unit: dollar)',
         gt=num(be())),
  D1=dict(q='Kolby Corp. is comparing two different capital structures, Plan I and Plan II. Plan I would result in 1,500 shares of stock '
            'and $20,000 in debt, while Plan II would result in 1,100 shares of stock and $30,000 in debt.Ignoring taxes, when will '
            'EPS be identical for Plans I and II? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the interest rate on the debt'), removed='10 percent'),
  D2=dict(q='Kolby Corp. is comparing two capital structures. The all-equity plan would have 2,300 shares outstanding. Plan I would '
            'result in 1,500 shares of stock and $20,000 in debt, and Plan II in 1,100 shares of stock and $30,000 in debt, with the '
            'debt proceeds used to repurchase shares at $20 per share. The interest rate on the debt is 10 percent.Ignoring taxes, '
            'when will EPS be identical for Plans I and II? (Unit: dollar)',
          gt=dict(type='contradiction', issue='at $20 per share, $20,000 buys back 1,000 shares (leaving 1,300, not 1,500) and '
                  '$30,000 buys back 1,500 (leaving 800, not 1,100); the share counts imply a $25 price'),
          violated=2300 - 20000 / 20 != 1500),
  D3=dict(q='Kolby Corp. is comparing two different capital structures, Plan I and Plan II. Plan I would result in 1,500 shares of stock '
            'and $20,000 in debt, while Plan II would result in 1,100 shares of stock and $30,000 in debt. The interest rate on the '
            'debt is 10 percent. Since Plan II uses more debt, its EPS is higher than Plan I\'s at every level of EBIT.Ignoring taxes, '
            'when will EPS be identical for Plans I and II? (Unit: dollar)',
          gt=dict(type='false_premise', issue='leverage raises EPS only above the break-even EBIT; below it Plan II has lower EPS',
                  value=be()), premise_value=None),
  D4=dict(q=NOW + 'Kolby Corp. is considering Plan II, which would result in 1,100 shares of stock and $30,000 in debt at an interest '
            'rate of 10 percent. Kolby pays the current U.S. federal statutory corporate income tax rate of 35 percent; ignore state '
            'taxes.What is EPS under Plan II if EBIT is $8,000? (Unit: dollar)',
          gt=dict(type='outdated', issue='the federal corporate rate has been a flat 21% since 2018 (TCJA), not 35%',
                  value=(8000 - 3000) * .79 / 1100, value_under_stated_rule=(8000 - 3000) * .65 / 1100)),
  D5=dict(q='Kolby Corp. is comparing two different capital structures, Plan I and Plan II. Plan I would result in 1,500 shares of stock '
            'and $20,000 in debt at 10 percent interest. Plan II would result in 1,100 shares of stock and $30,000 in debt; its lender '
            'has quoted 10 percent but may raise the rate to 12 percent because of the higher leverage.Ignoring taxes, when will EPS '
            'be identical for Plans I and II? (Unit: dollar)',
          gt=dict(type='assumption', about='Plan II\'s interest rate', options={'Plan II at 10%': be(), 'Plan II at 12%': be(.10, .12)})),
)

# =====================================================================
# 19  test_2972  invoice price with accrued interest
seed(id='test_2972', repro=865 + 37.5 * 3 / 6, params=['7.5', '865', 'three months'],
  E=dict(q='You purchase a bond with a coupon rate of 7.5 percent and a clean price of $865. The next semiannual coupon payment is due '
           'in three months. The bond was issued at par five years ago, it is callable, and the issuer\'s stock is up 8 percent this '
           'year.What is the invoice price of the bond? (Unit: dollar)',
         gt=num(883.75), distractors=[5, 8]),
  F=dict(q='I am buying my first individual corporate bond through my brokerage account, and the order screen shows two different '
           'prices, which is confusing me. The bond has a $1,000 face value and pays a 7.5 percent coupon, twice a year. The quoted '
           'clean price is $865. The next coupon payment is due in three months. The customer service person said something about '
           'accrued interest being added, but she could not tell me how much. How much will I actually pay for one bond, including '
           'accrued interest? (Unit: dollar)',
         gt=num(883.75)),
  D1=dict(q='You purchase a bond with a coupon rate of 7.5 percent, paid semiannually, and a clean price of $865.What is the invoice '
            'price of the bond? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the time since the last coupon (or until the next coupon)'), removed='three months'),
  D2=dict(q='You purchase a bond with a coupon rate of 7.5 percent and a clean price of $865. The next semiannual coupon payment is due '
            'in three months, and the accrued interest is $25.What is the invoice price of the bond? (Unit: dollar)',
          gt=dict(type='contradiction', issue='halfway through a $37.50 coupon period the accrued interest is $18.75, not $25'),
          violated=37.5 * 3 / 6 != 25),
  D3=dict(q='You purchase a bond with a coupon rate of 7.5 percent and a clean price of $865. The next semiannual coupon payment is due '
            'in three months. Since the quoted clean price already includes accrued interest, what is the invoice price of the bond? '
            '(Unit: dollar)',
          gt=dict(type='false_premise', issue='the clean price excludes accrued interest; invoice = clean + accrued', value=883.75),
          premise_value=865.0),
  D4=dict(q='It is Monday, August 3, 2026. You buy a U.S. corporate bond with a $1,000 face value and a 7.5 percent coupon paid '
            'semiannually on May 15 and November 15, at a clean price of $865. The trade settles on the standard T+2 settlement cycle '
            'for U.S. corporate bonds.How much accrued interest will you pay at settlement? (Unit: dollar)',
          gt=dict(type='outdated', issue='U.S. corporate bonds settle T+1 since 28 May 2024 (settlement Tue Aug 4, not Wed Aug 5)',
                  value=days_30_360(oneday('2026-05-15'), oneday('2026-08-04')) / 180 * 37.5,
                  value_under_stated_rule=days_30_360(oneday('2026-05-15'), oneday('2026-08-05')) / 180 * 37.5)),
  D5=dict(q='You purchase a bond with a coupon rate of 7.5 percent and a clean price of $865. The next coupon payment is due in three '
            'months.What is the invoice price of the bond? (Unit: dollar)',
          gt=dict(type='assumption', about='coupon frequency', options={'semiannual': 883.75, 'annual': 865 + 75 * 9 / 12})),
)

# =====================================================================
# 20  test_1405  constant-growth dividend model
gordon = lambda d0=1.60, g=.06, r=.12, next_div=False: (d0 if next_div else d0 * (1 + g)) / (r - g)
seed(id='test_1405', repro=gordon(), params=['$1.60', '6 percent', '12 percent'],
  E=dict(q='The Jackson-Timberlake Wardrobe Co. just paid a dividend of $1.60 per share on its stock. The dividends are expected to grow '
           'at a constant rate of 6 percent per year indefinitely. The company\'s earnings per share are $3.20, its payout ratio is '
           '50 percent, and its stock traded at $31 a year ago. Investors require a 12 percent return on The Jackson-Timberlake '
           'Wardrobe Co. stock.What is the current price of The Jackson-Timberlake Wardrobe Co. stock? (Unit: dollar)',
         gt=num(gordon()), distractors=[3.2, 50, 31]),
  F=dict(q='I have been reading about dividend investing and I am thinking about buying shares of The Jackson-Timberlake Wardrobe Co., '
           'a clothing company that has been around for decades. It just paid a dividend of $1.60 a share. Looking at its history '
           'and its business, I am comfortable assuming the dividend will keep growing at about 6 percent a year indefinitely. For a '
           'stock like this I would want a 12 percent return, since I could earn a decent amount on safer investments. I do not want '
           'to overpay just because the brand is familiar. Based on those assumptions, what is a fair price for one share today? '
           '(Unit: dollar)',
         gt=num(gordon())),
  D1=dict(q='The Jackson-Timberlake Wardrobe Co. just paid a dividend of $1.60 per share on its stock. Investors require a 12 percent '
            'return on the stock.What is the current price of The Jackson-Timberlake Wardrobe Co. stock? (Unit: dollar)',
          gt=dict(type='cannot_answer', missing='the dividend growth rate'), removed='6 percent'),
  D2=dict(q='The Jackson-Timberlake Wardrobe Co. just paid a dividend of $1.60 per share on its stock. The dividends are expected to '
            'grow at a constant rate of 13 percent per year indefinitely. Investors require a 12 percent return on the stock.What is '
            'the current price of The Jackson-Timberlake Wardrobe Co. stock? (Unit: dollar)',
          gt=dict(type='contradiction', issue='a perpetual growth rate (13%) at or above the required return (12%) has no finite '
                  'value; the constant-growth model does not apply'), violated=.13 >= .12),
  D3=dict(q='The Jackson-Timberlake Wardrobe Co. just paid a dividend of $1.60 per share on its stock. The dividends are expected to '
            'grow at a constant rate of 6 percent per year indefinitely, and investors require a 12 percent return. Since the '
            'dividend just paid is the one that drives the price, the price equals $1.60 divided by (12% - 6%).What is the current '
            'price of The Jackson-Timberlake Wardrobe Co. stock? (Unit: dollar)',
          gt=dict(type='false_premise', issue='the model uses next year\'s dividend D1 = 1.60 x 1.06', value=gordon()),
          premise_value=gordon(next_div=True)),
  D4=dict(q=NOW + 'The Jackson-Timberlake Wardrobe Co. just paid a dividend of $1.60 per share, and dividends are expected to grow at '
            '6 percent per year indefinitely. Investors require a return equal to the current 12-month USD LIBOR rate of 5 percent '
            'plus an equity premium of 7 percentage points.What is the current price of the stock? (Unit: dollar)',
          gt=dict(type='outdated', issue='USD LIBOR no longer exists', value=gordon(), value_under_stated_rule=gordon(),
                  flag_only=True)),
  D5=dict(q='The Jackson-Timberlake Wardrobe Co. pays a dividend of $1.60 per share on its stock. The dividends are expected to grow at '
            'a constant rate of 6 percent per year indefinitely. Investors require a 12 percent return on the stock.What is the '
            'current price of The Jackson-Timberlake Wardrobe Co. stock? (Unit: dollar)',
          gt=dict(type='assumption', about='whether $1.60 was just paid (D0) or is the next dividend (D1)',
                  options={'$1.60 just paid (D0)': gordon(), '$1.60 is next year\'s dividend (D1)': gordon(next_div=True)})),
)


# ---------------- checks and output ----------------
def rel(a, b):
    return abs(a - b) / max(abs(b), 1e-12)


def main():
    rows, problems = [], []
    for s in SEED_LIST:
        sd = SEEDS[s['id']]
        gt0 = float(sd['ground_truth'])
        if rel(s['repro'], gt0) > TOL:
            problems.append((s['id'], 'original not reproduced', s['repro'], gt0))
        versions = {'O': dict(q=sd['question'], gt=num(gt0))}
        versions.update({k: s[k] for k in ('E', 'F', 'D1', 'D2', 'D3', 'D4', 'D5')})
        for k, v in versions.items():
            gt, q, chk = v['gt'], v['q'], []
            if k == 'E':
                ok = rel(gt['value'], s['repro']) <= TOL and all(rel(x, gt['value']) > TOL for x in v['distractors'])
                chk.append(f"answer unchanged and no distractor equals it: {ok}")
            if k == 'F':
                missing = [p for p in s['params'] if p not in q]
                ok = rel(gt['value'], s['repro']) <= TOL and not missing
                chk.append(f"every given value appears in the text: {not missing}{'' if not missing else ' missing ' + str(missing)}")
            if k == 'D1':
                ok = v['removed'] not in q
                chk.append(f"removed value absent from text: {ok}")
            if k == 'D2':
                ok = bool(v['violated'])
                chk.append(f"contradiction verified by code: {ok}")
            if k == 'D3':
                pvv = v['premise_value']
                ok = pvv is None or rel(pvv, gt['value']) >= .01
                chk.append('answer if the false premise is accepted: ' + ('n/a' if pvv is None else f"{pvv:,.4f} ({100 * rel(pvv, gt['value']):.1f}% off)"))
            if k == 'D4':
                if gt.get('flag_only'):
                    ok = True; chk.append('flag only: the number is the same under the stated and current rules')
                else:
                    gap = rel(gt['value_under_stated_rule'], gt['value'])
                    ok = gap >= .01
                    chk.append(f"stated-rule answer {gt['value_under_stated_rule']:,.4f} is {100 * gap:.1f}% from current-rule answer")
            if k == 'D5':
                vals = list(gt['options'].values())
                spread = rel(max(vals), min(vals))
                ok = spread >= .01
                chk.append(f"options differ by {100 * spread:.1f}%")
            if k == 'O':
                ok = True
            if not ok:
                problems.append((s['id'], k, chk))
            rows.append(dict(item_id=f"{s['id']}_{k}", seed_id=s['id'], version=k, fin_capability=sd['fin_capability'],
                             topic=sd['topic'], question=q, gt=gt, checks=chk, check_ok=ok))
    with open('step2/batch160.jsonl', 'w') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(len(rows), 'items;', 'problems:', problems or 'none')
    write_md(rows)


NAMES = {'O': 'O 原题', 'E': 'E 加干扰信息', 'F': 'F 长段咨询', 'D1': 'D1 缺前提', 'D2': 'D2 前提矛盾',
         'D3': 'D3 错误前提', 'D4': 'D4 过时制度', 'D5': 'D5 需说明假设'}


def fmt(x):
    return f'{x:,.4f}'.rstrip('0').rstrip('.') if isinstance(x, (int, float)) else str(x)


def gt_text(gt):
    t = gt['type']
    if t == 'number':
        return fmt(gt['value']) + (f"（{gt['note']}）" if gt.get('note') else '')
    if t == 'cannot_answer':
        return f"算不出。缺：{gt['missing']}"
    if t == 'contradiction':
        return f"指出矛盾，不给数。矛盾：{gt['issue']}"
    if t == 'false_premise':
        return f"指出前提错误（{gt['issue']}），并给出正确值 {fmt(gt['value'])}"
    if t == 'outdated':
        tail = '（只考指出，数值与题中规则下相同）' if gt.get('flag_only') else f"；照题中旧规则算是 {fmt(gt['value_under_stated_rule'])}，判错"
        return f"指出过时（{gt['issue']}），按现行规则给出 {fmt(gt['value'])}{tail}"
    if t == 'assumption':
        opts = '；'.join(f"{k} → {fmt(v)}" for k, v in gt['options'].items())
        return f"写明关于「{gt['about']}」的假设，数值与假设一致。可接受：{opts}"


def write_md(rows):
    out = ['# 第二批：20 道种子 × 8 个版本 = 160 道（逐题）', '',
           '由 `scripts/step2_batch160.py` 生成，数据在 `batch160.jsonl`。所有数值由程序算出；每道种子题先复现了 XFinBench 原答案。', '']
    cur = None
    for r in rows:
        if r['seed_id'] != cur:
            cur = r['seed_id']
            out += [f"## {cur}　{r['fin_capability']}", '']
        out += [f"**{NAMES[r['version']]}**", '', f"> {r['question']}", '', f"- 正确回答：{gt_text(r['gt'])}"]
        out += [f"- 检查：{c}" for c in r['checks']]
        out.append('')
    open('step2/batch160_items.md', 'w').write('\n'.join(out))


if __name__ == '__main__':
    main()
