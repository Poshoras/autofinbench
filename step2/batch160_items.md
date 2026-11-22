# 第二批：20 道种子 × 8 个版本 = 160 道（逐题）

由 `scripts/step2_batch160.py` 生成，数据在 `batch160.jsonl`。所有数值由程序算出；每道种子题先复现了 XFinBench 原答案。

## test_1091　TR

**O 原题**

> Corpstein Credit Bank is offering 8.4 percent compounded daily on its savings accounts. Suppose you deposit $6,000 today.How much will you have in the account in 5 years? (Unit: dollar)

- 正确回答：9,131.33

**E 加干扰信息**

> Corpstein Credit Bank is offering 8.4 percent compounded daily on its savings accounts. Its rival, Second Federal, advertises 8.1 percent compounded monthly, inflation last year was 3.2 percent, and Corpstein charges a $15 fee to open a certificate of deposit, which does not apply to savings accounts. Suppose you deposit $6,000 today in a Corpstein savings account.How much will you have in the account in 5 years? (Unit: dollar)

- 正确回答：9,131.3281
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> Hi, I hope you can help me think something through. My grandmother passed away last spring and left me a little money. After paying for the funeral and a few of her outstanding bills, I ended up with $6,000 that I would like to put somewhere safe. I am 27, I rent a small apartment with a roommate, and I am planning to go back to school for a nursing degree in about five years, so I will not need to touch this money until then. I have been comparing banks near my office, and Corpstein Credit Bank is offering 8.4 percent compounded daily on its savings accounts, which is better than what my credit union pays. My plan is to deposit the whole $6,000 today and leave it alone until I enroll. If I do that, how much will I have in the account in 5 years? (Unit: dollar)

- 正确回答：9,131.3281
- 检查：every given value appears in the text: True

**D1 缺前提**

> Corpstein Credit Bank compounds interest daily on its savings accounts. Suppose you deposit $6,000 today.How much will you have in the account in 5 years? (Unit: dollar)

- 正确回答：算不出。缺：the interest rate on the savings account
- 检查：removed value absent from text: True

**D2 前提矛盾**

> Corpstein Credit Bank is offering 8.4 percent compounded daily on its savings accounts, which it advertises as an effective annual rate (EAR) of 8.0 percent. Suppose you deposit $6,000 today.How much will you have in the account in 5 years? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：8.4% compounded daily is an EAR of about 8.76%; an EAR below the quoted 8.4% is impossible
- 检查：contradiction verified by code: True

**D3 错误前提**

> Corpstein Credit Bank is offering 8.4 percent compounded daily on its savings accounts. Since daily compounding at a given annual rate produces the same balance as annual compounding at that rate, suppose you deposit $6,000 today.How much will you have in the account in 5 years? (Unit: dollar)

- 正确回答：指出前提错误（daily compounding gives more than annual compounding at the same quoted rate），并给出正确值 9,131.3281
- 检查：answer if the false premise is accepted: 8,980.4409 (1.7% off)

**D4 过时制度**

> It is November 2026. Corpstein Credit Bank's savings account pays the current 12-month USD LIBOR rate, which the bank quotes at 6.4 percent, plus 2.0 percentage points, compounded daily. Suppose you deposit $6,000 today.How much will you have in the account in 5 years? (Unit: dollar)

- 正确回答：指出过时（USD LIBOR no longer exists (all settings ceased; the last synthetic USD LIBOR was published on 30 Sep 2024); the reference rate would now be SOFR-based），按现行规则给出 9,131.3281（只考指出，数值与题中规则下相同）
- 检查：flag only: the number is the same under the stated and current rules

**D5 需说明假设**

> Corpstein Credit Bank is offering an 8.4 percent annual interest rate on its savings accounts. Suppose you deposit $6,000 today.How much will you have in the account in 5 years? (Unit: dollar)

- 正确回答：写明关于「compounding frequency」的假设，数值与假设一致。可接受：annual compounding → 8,980.4409；monthly compounding → 9,118.4177；daily compounding (365) → 9,131.3281；continuous compounding → 9,131.7693
- 检查：options differ by 1.7%

## test_3073　TR

**O 原题**

> You want to be a millionaire when you retire in 40 years. Assume you can earn an 11 percent annual return from your savings, and you consider making monthly deposits.How much do you have to save each month to be a millionaire if you wait 20 years before you begin your deposits? (Unit: dollar)

- 正确回答：1,155.22

**E 加干扰信息**

> You want to be a millionaire when you retire in 40 years. Assume you can earn an 11 percent annual return from your savings, and you consider making monthly deposits. Your current salary is $52,000, a friend's mutual fund returned 14 percent last year, and your employer's retirement plan charges a $35 annual account fee that it pays on your behalf.How much do you have to save each month to be a millionaire if you wait 20 years before you begin your deposits? (Unit: dollar)

- 正确回答：1,155.2173（same reading as XFinBench: 11% is an APR compounded monthly）
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> I am 25 and just started my first real job after college. My dad keeps telling me that I should aim to be a millionaire, meaning $1,000,000 in my account, by the time I retire at 65, which is 40 years from now. Honestly, I want to enjoy my twenties and thirties: travel, maybe buy a car, help my younger brother with tuition. So my plan is to wait 20 years before I start saving anything, and then make a deposit at the end of every month for the 20 years until I retire. My financial planner says a diversified portfolio can earn about 11 percent a year, compounded monthly. I know waiting is not ideal, but I want to see the number. How much would I have to put away each month, once I start in 20 years, to reach the million at retirement? (Unit: dollar)

- 正确回答：1,155.2173
- 检查：every given value appears in the text: True

**D1 缺前提**

> You want to be a millionaire when you retire in 40 years. You consider making monthly deposits, but you wait 20 years before you begin.How much do you have to save each month to be a millionaire? (Unit: dollar)

- 正确回答：算不出。缺：the rate of return on the savings
- 检查：removed value absent from text: True

**D2 前提矛盾**

> You want to be a millionaire when you retire in 40 years. Assume you can earn an 11 percent annual return, compounded monthly. You wait 20 years before you begin, and then make monthly deposits for 25 years until you retire.How much do you have to save each month to be a millionaire? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：20 years of waiting plus 25 years of deposits is 45 years, but retirement is in 40 years
- 检查：contradiction verified by code: True

**D3 错误前提**

> You want to be a millionaire when you retire in 40 years. Assume you can earn an 11 percent annual return, compounded monthly, and you make monthly deposits. Since waiting 20 years before you start only halves the number of deposits, the monthly amount you need is about twice what it would be if you started today.How much do you have to save each month to be a millionaire if you wait 20 years before you begin your deposits? (Unit: dollar)

- 正确回答：指出前提错误（the required deposit is about 10 times, not 2 times, the start-now amount, because the money loses 20 years of compounding），并给出正确值 1,155.2173
- 检查：answer if the false premise is accepted: 232.5547 (79.9% off)

**D4 过时制度**

> It is November 2026. You want to be a millionaire when you retire in 40 years. Your savings will earn the current 12-month USD LIBOR rate of 5 percent plus 6 percentage points per year, compounded monthly, and you make monthly deposits.How much do you have to save each month to be a millionaire if you wait 20 years before you begin your deposits? (Unit: dollar)

- 正确回答：指出过时（USD LIBOR no longer exists (ceased; last synthetic setting 30 Sep 2024)），按现行规则给出 1,155.2173（只考指出，数值与题中规则下相同）
- 检查：flag only: the number is the same under the stated and current rules

**D5 需说明假设**

> You want to be a millionaire when you retire in 40 years. Assume you can earn an 11 percent annual return, compounded monthly, and that inflation will average 3 percent per year. You wait 20 years before you begin making monthly deposits.How much do you have to save each month to be a millionaire? (Unit: dollar)

- 正确回答：写明关于「whether "millionaire" means $1 million in future dollars or in today's purchasing power」的假设，数值与假设一致。可接受：$1,000,000 nominal → 1,155.2173；$1,000,000 in today's dollars (target x 1.03^40) → 3,768.3624
- 检查：options differ by 226.2%

## test_63　TR

**O 原题**

> A 10% coupon bond has a face value of $1000, a 12.25% yield to maturity, and eight years to maturity.What is the price of the bond? (Unit: dollar)

- 正确回答：889.2

**E 加干扰信息**

> A 10% coupon bond has a face value of $1000, a 12.25% yield to maturity, and eight years to maturity. The bond was issued two years ago at par, when market yields were 10%; its current yield is 11.25%; and the issuer's common stock trades at $42.What is the price of the bond? (Unit: dollar)

- 正确回答：889.1977
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> My broker called this morning about a corporate bond he thinks would suit my retirement account. I am not very experienced with bonds, so I wrote down what he said: it has a face value of $1,000, pays a 10% coupon once a year, and matures in eight years. He mentioned that the company had a rough couple of years but is stable now, and that the bond's yield to maturity is 12.25%, which is why it looks attractive compared with my CDs. Before I call him back I want to know whether his quote is reasonable. Based on those numbers, what price should one of these bonds sell for? (Unit: dollar)

- 正确回答：889.1977
- 检查：every given value appears in the text: True

**D1 缺前提**

> A 10% coupon bond has a face value of $1000 and eight years to maturity. Coupons are paid annually.What is the price of the bond? (Unit: dollar)

- 正确回答：算不出。缺：the yield to maturity (market discount rate)
- 检查：removed value absent from text: True

**D2 前提矛盾**

> A 10% coupon bond with a face value of $1000 and eight years to maturity trades at a premium to its face value, and its yield to maturity is 12.25%. Coupons are paid annually.What is the price of the bond? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：a bond whose coupon rate (10%) is below its yield (12.25%) must trade at a discount, not a premium
- 检查：contradiction verified by code: True

**D3 错误前提**

> A 10% coupon bond has a face value of $1000, a 12.25% yield to maturity, and eight years to maturity, with annual coupons. Since its coupon rate is below its yield to maturity, the bond trades at a premium.What is the price of the bond? (Unit: dollar)

- 正确回答：指出前提错误（coupon below yield means a discount bond），并给出正确值 889.1977
- 检查：answer if the false premise is accepted: n/a

**D4 过时制度**

> It is November 2026. A 10% coupon bond has a face value of $1000, eight years to maturity, and annual coupons. Its yield is set at the current 12-month USD LIBOR rate of 7.25% plus a credit spread of 5.00 percentage points.What is the price of the bond? (Unit: dollar)

- 正确回答：指出过时（USD LIBOR no longer exists; a current spread would be quoted over SOFR or Treasuries），按现行规则给出 889.1977（只考指出，数值与题中规则下相同）
- 检查：flag only: the number is the same under the stated and current rules

**D5 需说明假设**

> A bond pays a 10% coupon annually, has a 12.25% yield to maturity, and has eight years to maturity.What is the price of the bond? (Unit: dollar)

- 正确回答：写明关于「face value (price per $1,000 or per $100 of face value)」的假设，数值与假设一致。可接受：per $1,000 face → 889.1977；per $100 face → 88.9198
- 检查：options differ by 900.0%

## test_2545　TR

**O 原题**

> Spears, Inc., has an odd dividend policy. The company has just paid a dividend of $7 per share and has announced that it will increase the dividend by $4 per share for each of the next four years, and then never pay another dividend. The required return on the company's stock is 11 percent.How much will you pay for a share of Spears, Inc. today? (Unit: dollar)

- 正确回答：51.13

**E 加干扰信息**

> Spears, Inc., has an odd dividend policy. The company has just paid a dividend of $7 per share and has announced that it will increase the dividend by $4 per share for each of the next four years, and then never pay another dividend. Spears earned $9.50 per share last year, the industry's average price-earnings ratio is 14, and the stock's beta is 1.3. The required return on the company's stock is 11 percent.How much will you pay for a share of Spears, Inc. today? (Unit: dollar)

- 正确回答：51.1277
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> My uncle owns shares in Spears, Inc., a family-run company in his town, and he has offered to sell me some of them. The company is a bit unusual. It has just paid a dividend of $7 a share, and the founder has announced that the dividend will go up by $4 a share in each of the next four years. After that, the company will stop paying dividends altogether, because the founder plans to wind the business down and the remaining assets are expected to be worth nothing. My uncle is not in a hurry, but I want to make him a fair offer. For a holding like this I would want to earn at least 11 percent a year. What is the most I should pay per share today? (Unit: dollar)

- 正确回答：51.1277
- 检查：every given value appears in the text: True

**D1 缺前提**

> Spears, Inc., has an odd dividend policy. The company has just paid a dividend of $7 per share and has announced that it will increase the dividend by $4 per share for each of the next four years, and then never pay another dividend.How much will you pay for a share of Spears, Inc. today? (Unit: dollar)

- 正确回答：算不出。缺：the required return (discount rate)
- 检查：removed value absent from text: True

**D2 前提矛盾**

> Spears, Inc., has just paid a dividend of $7 per share and has announced that it will increase the dividend by $4 per share for each of the next four years, so that the dividend in year four will be $19. It will then never pay another dividend. The required return is 11 percent.How much will you pay for a share of Spears, Inc. today? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：$7 plus four $4 increases is $23 in year four, not $19
- 检查：contradiction verified by code: True

**D3 错误前提**

> Spears, Inc., has just paid a dividend of $7 per share and will increase the dividend by $4 per share for each of the next four years, and then never pay another dividend. The required return is 11 percent. Since the company stops paying dividends after year four, the price today is simply the sum of the four upcoming dividends.How much will you pay for a share of Spears, Inc. today? (Unit: dollar)

- 正确回答：指出前提错误（future dividends must be discounted at the required return），并给出正确值 51.1277
- 检查：answer if the false premise is accepted: 68.0000 (33.0% off)

**D4 过时制度**

> It is November 2026. Spears, Inc., has just paid a dividend of $7 per share and will increase the dividend by $4 per share for each of the next four years, and then never pay another dividend. Investors require a return equal to the current 12-month USD LIBOR rate of 5 percent plus an equity premium of 6 percentage points.How much will you pay for a share of Spears, Inc. today? (Unit: dollar)

- 正确回答：指出过时（USD LIBOR no longer exists），按现行规则给出 51.1277（只考指出，数值与题中规则下相同）
- 检查：flag only: the number is the same under the stated and current rules

**D5 需说明假设**

> Spears, Inc., will pay a dividend of $7 per share this year, then increase it by $4 per share for each of the next four years, and then never pay another dividend. The required return is 11 percent.How much will you pay for a share of Spears, Inc. today? (Unit: dollar)

- 正确回答：写明关于「when the $7 dividend is paid」的假设，数值与假设一致。可接受：$7 paid today (cum-dividend), then $11-$23 in years 1-4 → 58.1277；$7 in one year, then $11-$23 in years 2-5 → 52.3673
- 检查：options differ by 11.0%

## test_2275　TR

**O 原题**

> A corporate bond pays a 7% coupon on January 7 and July 7. The time frame is between July 7, 2014, and August 8, 2014.How much interest accrues per $100 of principal for a corporate bond between July 7, 2014, and August 8, 2014? (Unit: dollar)

- 正确回答：0.6028

**E 加干扰信息**

> A corporate bond pays a 7% coupon on January 7 and July 7. The bond's clean price is 98.50, its yield to maturity is 7.4%, and it matures in 2029. The time frame is between July 7, 2014, and August 8, 2014.How much interest accrues per $100 of principal for a corporate bond between July 7, 2014, and August 8, 2014? (Unit: dollar)

- 正确回答：0.6028
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> Last summer my father bought a corporate bond through his bank, and I am helping him check the trade confirmation because the numbers confuse him. The bond pays a 7% annual coupon in two installments, on January 7 and July 7 each year. He is a retired machinist and very careful with money, so he wants to understand every line. The part we are stuck on is the interest that had built up after the July 7, 2014 coupon was paid. How much interest accrues per $100 of principal on this corporate bond between July 7, 2014, and August 8, 2014? (Unit: dollar)

- 正确回答：0.6028
- 检查：every given value appears in the text: True

**D1 缺前提**

> A corporate bond pays coupons on January 7 and July 7.How much interest accrues per $100 of principal between July 7, 2014, and August 8, 2014? (Unit: dollar)

- 正确回答：算不出。缺：the coupon rate
- 检查：removed value absent from text: True

**D2 前提矛盾**

> A corporate bond pays a 7% coupon on January 7 and July 7. The period between July 7, 2014, and August 8, 2014, counts as 45 days under the bond's day count convention.How much interest accrues per $100 of principal over that period? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：the period is 31 days under 30/360 (32 actual days), not 45
- 检查：contradiction verified by code: True

**D3 错误前提**

> A corporate bond pays a 7% coupon on January 7 and July 7. Because U.S. corporate bonds accrue interest on an actual/actual basis, how much interest accrues per $100 of principal between January 7, 2015, and March 1, 2015? (Unit: dollar)

- 正确回答：指出前提错误（U.S. corporate bonds use 30/360; actual/actual is used for Treasuries），并给出正确值 1.05
- 检查：answer if the false premise is accepted: 1.0249 (2.4% off)

**D4 过时制度**

> It is Monday, August 3, 2026. You buy a U.S. corporate bond that pays a 7% coupon on January 7 and July 7, and the trade settles on the standard T+2 settlement cycle for U.S. corporate bonds.How much accrued interest per $100 of principal will you pay at settlement? (Unit: dollar)

- 正确回答：指出过时（U.S. corporate bonds settle T+1 since 28 May 2024, so settlement is Tue Aug 4, not Wed Aug 5），按现行规则给出 0.525；照题中旧规则算是 0.5444，判错
- 检查：stated-rule answer 0.5444 is 3.7% from current-rule answer

**D5 需说明假设**

> A bond pays a 7% coupon on January 7 and July 7.How much interest accrues per $100 of principal between January 7, 2015, and March 1, 2015? (Unit: dollar)

- 正确回答：写明关于「day count convention (depends on the type of bond)」的假设，数值与假设一致。可接受：30/360 (corporate) → 1.05；actual/actual (Treasury) → 1.0249
- 检查：options differ by 2.5%

## test_1102　SP; TR

**O 原题**

> A stock price is currently $40. Over each of the next two three-month periods, it is expected to go up by 10% or down by 10%. The risk-free interest rate is 12% per annum with continuous compounding.What is the value of a six-month European put option with a strike price of $42? (Unit: dollar)

- 正确回答：2.118

**E 加干扰信息**

> A stock price is currently $40. Over each of the next two three-month periods, it is expected to go up by 10% or down by 10%. The risk-free interest rate is 12% per annum with continuous compounding. The stock's expected return is 15% per annum, its historical volatility is 18% per annum, and its next earnings announcement is in five weeks.What is the value of a six-month European put option with a strike price of $42? (Unit: dollar)

- 正确回答：2.1185
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> I work for a mid-sized tech company and a good part of my savings is in company stock, currently $40 a share. With the layoffs in our industry I am nervous, so I am thinking about buying protection. My brokerage offers a six-month European put with a $42 strike. Their pricing tool uses a simple model: over each of the next two three-month periods the stock either goes up 10% or goes down 10%, and the risk-free rate is 12% a year with continuous compounding. My wife thinks puts are a waste of money, and I want to show her what the fair price is before we argue about it. Under that model, what is the put worth? (Unit: dollar)

- 正确回答：2.1185
- 检查：every given value appears in the text: True

**D1 缺前提**

> A stock price is currently $40. Over each of the next two three-month periods, it is expected to go up by 10% or down by 10%.What is the value of a six-month European put option with a strike price of $42? (Unit: dollar)

- 正确回答：算不出。缺：the risk-free interest rate
- 检查：removed value absent from text: True

**D2 前提矛盾**

> A stock price is currently $40. Over each of the next two three-month periods, it is expected to go up by 2% or down by 10%. The risk-free interest rate is 12% per annum with continuous compounding.What is the value of a six-month European put option with a strike price of $42? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：the up factor 1.02 is below the risk-free growth e^(0.12*0.25)=1.030, so the tree admits arbitrage (risk-neutral probability above 1)
- 检查：contradiction verified by code: True

**D3 错误前提**

> A stock price is currently $40. Over each of the next two three-month periods, it is expected to go up by 10% or down by 10%. The risk-free interest rate is 12% per annum with continuous compounding. Since the stock is equally likely to go up or down, the probability of an up move used to value the option is 0.5.What is the value of a six-month European put option with a strike price of $42? (Unit: dollar)

- 正确回答：指出前提错误（valuation uses the risk-neutral probability (about 0.652), not the real-world 0.5），并给出正确值 2.1185
- 检查：answer if the false premise is accepted: 3.3904 (60.0% off)

**D4 过时制度**

> It is November 2026. A stock price is currently $40. Over each of the next two three-month periods, it is expected to go up by 10% or down by 10%. The risk-free rate, taken as the current six-month USD LIBOR rate, is 12% per annum with continuous compounding.What is the value of a six-month European put option with a strike price of $42? (Unit: dollar)

- 正确回答：指出过时（USD LIBOR no longer exists; the risk-free proxy would now be SOFR or Treasury rates），按现行规则给出 2.1185（只考指出，数值与题中规则下相同）
- 检查：flag only: the number is the same under the stated and current rules

**D5 需说明假设**

> A stock price is currently $40. Over each of the next two three-month periods, it is expected to go up by 10% or down by 10%. The risk-free interest rate is 12% per annum with continuous compounding.What is the value of a six-month put option with a strike price of $42? (Unit: dollar)

- 正确回答：写明关于「exercise style」的假设，数值与假设一致。可接受：European → 2.1185；American → 2.5374
- 检查：options differ by 19.8%

## test_1716　SP; TR

**O 原题**

> The volatility of a non-dividend-paying stock, whose price is $78, is 30%. The risk-free rate is 3% per annum (continuously compounded) for all maturities. A two-month time step is used for calculations.What is the value of a four-month European call option with a strike price of $80 given by a two-step binomial tree? (Unit: dollar)

- 正确回答：4.67

**E 加干扰信息**

> The volatility of a non-dividend-paying stock, whose price is $78, is 30%. The risk-free rate is 3% per annum (continuously compounded) for all maturities. A two-month time step is used for calculations. The stock's expected return is 9% per annum, analysts' 12-month price target is $90, and the company has 250 million shares outstanding.What is the value of a four-month European call option with a strike price of $80 given by a two-step binomial tree? (Unit: dollar)

- 正确回答：4.6677
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> I have been following a non-dividend-paying stock that trades at $78, and I am considering buying a four-month European call with an $80 strike because I think a new product launch could push the price up. I am taking an online derivatives course, and the instructor showed us how to value options with a binomial tree. The stock's volatility is about 30% a year, and the risk-free rate is 3% a year, continuously compounded, for all maturities. If I build a two-step binomial tree with two-month steps, using the standard up and down factors from the volatility, what value does it give for the call? (Unit: dollar)

- 正确回答：4.6677
- 检查：every given value appears in the text: True

**D1 缺前提**

> A non-dividend-paying stock's price is $78. The risk-free rate is 3% per annum (continuously compounded) for all maturities. A two-month time step is used for calculations.What is the value of a four-month European call option with a strike price of $80 given by a two-step binomial tree? (Unit: dollar)

- 正确回答：算不出。缺：the volatility (or the up and down factors)
- 检查：removed value absent from text: True

**D2 前提矛盾**

> A non-dividend-paying stock's price is $78. In each two-month step it moves up by a factor of 1.13 or down by a factor of 0.88, the risk-free rate is 3% per annum (continuously compounded), and the risk-neutral probability of an up move is 0.70.What is the value of a four-month European call option with a strike price of $80 given by a two-step binomial tree? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：with these factors and rate the risk-neutral probability must be (e^(0.005)-0.88)/(1.13-0.88) = 0.50, not 0.70
- 检查：contradiction verified by code: True

**D3 错误前提**

> The volatility of a non-dividend-paying stock, whose price is $78, is 30%. The risk-free rate is 3% per annum (continuously compounded). A two-month time step is used. Because the call is out of the money today (the stock price is below the strike), its value is zero.What is the value of a four-month European call option with a strike price of $80 given by a two-step binomial tree? (Unit: dollar)

- 正确回答：指出前提错误（an out-of-the-money option still has time value），并给出正确值 4.6677
- 检查：answer if the false premise is accepted: 0.0000 (100.0% off)

**D4 过时制度**

> It is November 2026. The volatility of a non-dividend-paying stock, whose price is $78, is 30%. The risk-free rate, taken as the current 3-month USD LIBOR rate, is 3% per annum (continuously compounded). A two-month time step is used.What is the value of a four-month European call option with a strike price of $80 given by a two-step binomial tree? (Unit: dollar)

- 正确回答：指出过时（USD LIBOR no longer exists），按现行规则给出 4.6677（只考指出，数值与题中规则下相同）
- 检查：flag only: the number is the same under the stated and current rules

**D5 需说明假设**

> The volatility of a stock whose price is $78 is 30%. The risk-free rate is 3% per annum (continuously compounded). The company may pay a dividend of $1.50 per share in three months, but the board has not decided. A two-month time step is used.What is the value of a four-month European call option with a strike price of $80 given by a two-step binomial tree? (Unit: dollar)

- 正确回答：写明关于「whether the $1.50 dividend is paid」的假设，数值与假设一致。可接受：no dividend → 4.6677；dividend paid (tree on S minus PV of dividend) → 4.2159
- 检查：options differ by 10.7%

## test_1822　SP

**O 原题**

> A stock price is currently $40. At the end of one month, it will be either $42 or $38. The risk-free interest rate is 8% per annum with continuous compounding.What is the value of a one-month European call option with a strike price of $39? (Unit: dollar)

- 正确回答：1.69

**E 加干扰信息**

> A stock price is currently $40. At the end of one month, it will be either $42 or $38. The risk-free interest rate is 8% per annum with continuous compounding. Analysts estimate a 70% chance that the stock will rise to $42, and the stock's average daily trading volume is 2 million shares.What is the value of a one-month European call option with a strike price of $39? (Unit: dollar)

- 正确回答：1.6894
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> I trade a little on the side and I am trying to understand how options are priced instead of just guessing. There is a stock I follow that is at $40 right now. For a simple exercise, assume that one month from now it will be at either $42 or $38, nothing in between. The risk-free rate is 8% per year with continuous compounding. I want to price a one-month European call with a $39 strike using no-arbitrage reasoning, the way the textbook does with a replicating portfolio. My roommate says the answer is just the average payoff, but I do not think that is right. What is the call worth? (Unit: dollar)

- 正确回答：1.6894
- 检查：every given value appears in the text: True

**D1 缺前提**

> A stock price is currently $40. At the end of one month, it will be either $42 or $38.What is the value of a one-month European call option with a strike price of $39? (Unit: dollar)

- 正确回答：算不出。缺：the risk-free interest rate
- 检查：removed value absent from text: True

**D2 前提矛盾**

> A stock price is currently $40. At the end of one month, it will be either $42 or $41. The risk-free interest rate is 8% per annum with continuous compounding.What is the value of a one-month European call option with a strike price of $39? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：both outcomes beat the risk-free growth of $40 (to about $40.27), so the setup admits arbitrage
- 检查：contradiction verified by code: True

**D3 错误前提**

> A stock price is currently $40. At the end of one month, it will be either $42 or $38. The risk-free interest rate is 8% per annum with continuous compounding. Since the real-world probability of an up move is 70%, the option's value is its expected payoff of 0.7 x $3, discounted at the risk-free rate.What is the value of a one-month European call option with a strike price of $39? (Unit: dollar)

- 正确回答：指出前提错误（no-arbitrage value uses the risk-neutral probability, not the real-world one），并给出正确值 1.6894
- 检查：answer if the false premise is accepted: 2.0860 (23.5% off)

**D4 过时制度**

> It is November 2026. A stock price is currently $40. At the end of one month, it will be either $42 or $38. The risk-free rate, taken as the current 1-month USD LIBOR rate, is 8% per annum with continuous compounding.What is the value of a one-month European call option with a strike price of $39? (Unit: dollar)

- 正确回答：指出过时（USD LIBOR no longer exists），按现行规则给出 1.6894（只考指出，数值与题中规则下相同）
- 检查：flag only: the number is the same under the stated and current rules

**D5 需说明假设**

> A stock price is currently $40. At the end of one month, it will be either $42 or $38. The risk-free interest rate is 8% per annum with continuous compounding.What is the value of a one-month European option with a strike price of $39? (Unit: dollar)

- 正确回答：写明关于「call or put」的假设，数值与假设一致。可接受：call → 1.6894；put → 0.4302
- 检查：options differ by 292.7%

## test_1137　SP

**O 原题**

> A four-month call option on a non-dividend-paying stock has a stock price of $28, a strike price of $25, and the risk-free interest rate is 8% per annum.What is a lower bound for the price of the call option? (Unit: dollar)

- 正确回答：3.66

**E 加干扰信息**

> A four-month call option on a non-dividend-paying stock has a stock price of $28, a strike price of $25, and the risk-free interest rate is 8% per annum. The call currently trades at $4.20, the stock's volatility is 35%, and its beta is 0.9.What is a lower bound for the price of the call option? (Unit: dollar)

- 正确回答：3.6579
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> I am studying for a finance exam and also trying to apply it to my own small trading account, so I want to get this right. There is a four-month call option on a stock that does not pay dividends. The stock is at $28, the strike is $25, and the risk-free rate is 8% per year with continuous compounding. My study partner says the call can never trade below $3 because that is what you would get by exercising now, but the textbook talks about a tighter bound that uses the present value of the strike. What is the lower bound for the price of this call, in the textbook sense? (Unit: dollar)

- 正确回答：3.6579
- 检查：every given value appears in the text: True

**D1 缺前提**

> A four-month call option on a non-dividend-paying stock has a strike price of $25, and the risk-free interest rate is 8% per annum.What is the standard no-arbitrage lower bound for the price of the call option? (Unit: dollar)

- 正确回答：算不出。缺：the current stock price
- 检查：removed value absent from text: True

**D2 前提矛盾**

> A four-month call option on a non-dividend-paying stock has a stock price of $28, a strike price of $25, and the risk-free interest rate is 8% per annum; the call is currently 10% out of the money.What is a lower bound for the price of the call option? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：with the stock at $28 above the $25 strike, the call is in the money, not out of the money
- 检查：contradiction verified by code: True

**D3 错误前提**

> A four-month call option on a non-dividend-paying stock has a stock price of $28, a strike price of $25, and the risk-free interest rate is 8% per annum. Because the stock pays no dividends, the lower bound for the call is simply the stock price minus the strike price.What is the lower bound for the price of the call option? (Unit: dollar)

- 正确回答：指出前提错误（the bound is S minus the present value of K, which is tighter than S minus K），并给出正确值 3.6579
- 检查：answer if the false premise is accepted: 3.0000 (18.0% off)

**D4 过时制度**

> It is November 2026. A four-month call option on a non-dividend-paying stock has a stock price of $28 and a strike price of $25. The risk-free rate, taken as the current 3-month USD LIBOR rate, is 8% per annum.What is a lower bound for the price of the call option? (Unit: dollar)

- 正确回答：指出过时（USD LIBOR no longer exists），按现行规则给出 3.6579（只考指出，数值与题中规则下相同）
- 检查：flag only: the number is the same under the stated and current rules

**D5 需说明假设**

> A four-month call option on a stock has a stock price of $28, a strike price of $25, and the risk-free interest rate is 8% per annum with continuous compounding. The company may pay a dividend of $1.00 per share in two months; the board has not yet decided.What is a lower bound for the price of the call option? (Unit: dollar)

- 正确回答：写明关于「whether the dividend is paid」的假设，数值与假设一致。可接受：no dividend → 3.6579；$1.00 dividend paid → 2.6711
- 检查：options differ by 36.9%

## test_1907　SP

**O 原题**

> Suppose that the risk-free interest rate is 10% per annum with continuous compounding and that the dividend yield on a stock index is 4% per annum. The index is standing at 400, and the futures price for a contract deliverable in four months is 405.What is the theoretical futures price for a contract deliverable in four months? (Unit: dollar)

- 正确回答：408.08

**E 加干扰信息**

> Suppose that the risk-free interest rate is 10% per annum with continuous compounding and that the dividend yield on a stock index is 4% per annum. The index is standing at 400, and the futures price for a contract deliverable in four months is 405. The index's volatility is 18%, it rose 12% over the past year, and a six-month contract trades at 413.What is the theoretical futures price for a contract deliverable in four months? (Unit: dollar)

- 正确回答：408.0805
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> I manage the investments of a small family office, and we use stock index futures to adjust our equity exposure. Before we roll our position I want to check whether the futures are fairly priced. The index is at 400 today. The risk-free rate is 10% a year with continuous compounding, and the index has a dividend yield of 4% a year, also continuous. Our broker's screen is down, so I cannot see the quoted futures price right now, and I just want the theoretical value from cost of carry. What should the futures price be for a contract deliverable in four months? (Unit: dollar)

- 正确回答：408.0805
- 检查：every given value appears in the text: True

**D1 缺前提**

> Suppose that the dividend yield on a stock index is 4% per annum. The index is standing at 400.What is the theoretical futures price for a contract deliverable in four months? (Unit: dollar)

- 正确回答：算不出。缺：the risk-free interest rate
- 检查：removed value absent from text: True

**D2 前提矛盾**

> Suppose that the risk-free interest rate is 10% per annum with continuous compounding and that the dividend yield on a stock index is 4% per annum. The index is standing at 400 and its constituents pay dividends totaling 25 index points per year.What is the theoretical futures price for a contract deliverable in four months? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：25 points a year on an index of 400 is a 6.25% yield, not 4%
- 检查：contradiction verified by code: True

**D3 错误前提**

> Suppose that the risk-free interest rate is 10% per annum with continuous compounding and that the dividend yield on a stock index is 4% per annum. The index is standing at 400. Since dividends on the index raise the futures price above what it would be without dividends, what is the theoretical futures price for a contract deliverable in four months? (Unit: dollar)

- 正确回答：指出前提错误（dividends lower the futures price (F = S e^{(r-q)T})），并给出正确值 408.0805
- 检查：answer if the false premise is accepted: 419.1091 (2.7% off)

**D4 过时制度**

> It is November 2026. The risk-free interest rate, taken as the current 4-month USD LIBOR rate, is 10% per annum with continuous compounding, and the dividend yield on a stock index is 4% per annum. The index is standing at 400.What is the theoretical futures price for a contract deliverable in four months? (Unit: dollar)

- 正确回答：指出过时（USD LIBOR no longer exists (and there was never a 4-month tenor)），按现行规则给出 408.0805（只考指出，数值与题中规则下相同）
- 检查：flag only: the number is the same under the stated and current rules

**D5 需说明假设**

> Suppose that the risk-free interest rate is 10% per annum and the dividend yield on a stock index is 4% per annum. The index is standing at 400.What is the theoretical forward price for a contract deliverable in three years? (Unit: dollar)

- 正确回答：写明关于「compounding convention of the quoted rates」的假设，数值与假设一致。可接受：continuous compounding → 478.8869；annual compounding → 473.3017
- 检查：options differ by 1.2%

## test_674　TU

**O 原题**

> Parker & Stone, Inc., is looking at setting up a new manufacturing plant in South Park to produce garden tools. The company bought some land six years ago for $5 million in anticipation of using it as a warehouse and distribution site, but the company has since decided to rent these facilities from a competitor instead. If the land were sold today, the company would net $5.3 million. The new plant will cost $11.6 million to build, and the site requires $425,000 worth of grading before it is suitable for construction.What is the proper cash flow amount to use as the initial investment in fixed assets when evaluating this project? (Unit: dollar)

- 正确回答：17,325,000

**E 加干扰信息**

> Parker & Stone, Inc., is looking at setting up a new manufacturing plant in South Park to produce garden tools. The company bought some land six years ago for $5 million in anticipation of using it as a warehouse and distribution site, but the company has since decided to rent these facilities from a competitor instead. If the land were sold today, the company would net $5.3 million. The new plant will cost $11.6 million to build, and the site requires $425,000 worth of grading before it is suitable for construction. Last year the company spent $250,000 on a feasibility study for the plant, its WACC is 11 percent, and the plant will be depreciated over 20 years.What is the proper cash flow amount to use as the initial investment in fixed assets when evaluating this project? (Unit: dollar)

- 正确回答：17,325,000
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> I am the controller at Parker & Stone, a family-owned maker of garden tools, and the owners asked me to put together the numbers for a new plant in South Park. Some background: six years ago we bought a plot of land for $5 million because we planned to build a warehouse and distribution center there. We later decided to rent warehouse space from a competitor instead, so the land has been sitting empty. A broker tells me that if we sold it today we would net $5.3 million. Now the idea is to build the plant on that land. The construction quote is $11.6 million, and the site needs $425,000 of grading before construction can start. What cash flow should I use as the initial investment in fixed assets when evaluating the plant? (Unit: dollar)

- 正确回答：17,325,000
- 检查：every given value appears in the text: True

**D1 缺前提**

> Parker & Stone, Inc., is looking at setting up a new manufacturing plant in South Park to produce garden tools. The company bought some land six years ago for $5 million in anticipation of using it as a warehouse and distribution site, but the company has since decided to rent these facilities from a competitor instead. The new plant will be built on this land; it will cost $11.6 million to build, and the site requires $425,000 worth of grading.What is the proper cash flow amount to use as the initial investment in fixed assets when evaluating this project? (Unit: dollar)

- 正确回答：算不出。缺：what the land could be sold for today (its opportunity cost); the $5 million paid is sunk
- 检查：removed value absent from text: True

**D2 前提矛盾**

> Parker & Stone, Inc., bought some land six years ago for $5 million. If the land were sold today, the company would net $5.3 million, a loss of $700,000 relative to what it paid. The company plans to build a new plant on the land instead; the plant will cost $11.6 million, and the site requires $425,000 worth of grading.What is the proper cash flow amount to use as the initial investment in fixed assets when evaluating this project? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：selling for $5.3 million after paying $5 million is a $300,000 gain, not a $700,000 loss
- 检查：contradiction verified by code: True

**D3 错误前提**

> Parker & Stone, Inc., bought some land six years ago for $5 million; if sold today, it would net $5.3 million. The company plans to build a new plant on the land; the plant will cost $11.6 million, and the site requires $425,000 worth of grading. Since the land was bought six years ago, its cost is sunk and the land should be left out of the initial investment.What is the proper cash flow amount to use as the initial investment in fixed assets when evaluating this project? (Unit: dollar)

- 正确回答：指出前提错误（the historical cost is sunk, but the land's current value is an opportunity cost and must be included），并给出正确值 17,325,000
- 检查：answer if the false premise is accepted: 12,025,000.0000 (30.6% off)

**D4 过时制度**

> It is November 2026. Parker & Stone, Inc., bought some land six years ago for $5 million. If the land were sold today, the company would receive $5.3 million before taxes. The $300,000 gain would be taxed at the current U.S. federal corporate income tax rate of 35 percent; ignore state taxes.How much federal tax would the sale of the land generate? (Unit: dollar)

- 正确回答：指出过时（the federal corporate rate has been a flat 21% since 2018 (TCJA), not 35%），按现行规则给出 63,000；照题中旧规则算是 105,000，判错
- 检查：stated-rule answer 105,000.0000 is 66.7% from current-rule answer

**D5 需说明假设**

> Parker & Stone, Inc., bought some land six years ago for $5 million. Brokers estimate the land would sell today for between $5.0 million and $5.6 million, net of selling costs. The company plans to build a new plant on the land instead; the plant will cost $11.6 million, and the site requires $425,000 worth of grading.What is the proper cash flow amount to use as the initial investment in fixed assets when evaluating this project? (Unit: dollar)

- 正确回答：写明关于「which land value in the $5.0-5.6 million range to use; the answer must equal $12,025,000 plus the stated land value」的假设，数值与假设一致。可接受：land at $5.0M → 17,025,000；land at $5.3M (midpoint) → 17,325,000；land at $5.6M → 17,625,000
- 检查：options differ by 3.5%

## test_945　FF

**O 原题**

> If the Fed buys $1 million of bonds from the First National Bank, and an additional 10% of any deposit is held as excess reserves, the reserve requirement ratio is 10%.What is the total increase in checkable deposits? (Unit: dollar)

- 正确回答：5,000,000

**E 加干扰信息**

> If the Fed buys $1 million of bonds from the First National Bank, and an additional 10% of any deposit is held as excess reserves, the reserve requirement ratio is 10%. The federal funds rate is 4.25%, the First National Bank has $250 million in total assets, and the discount rate is 4.75%.What is the total increase in checkable deposits? (Unit: dollar)

- 正确回答：5,000,000
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> I am writing an explainer for our college newspaper about how the Fed creates money, and I want to use a concrete example that I can check. Suppose the Fed buys $1 million of bonds from the First National Bank. Banks are required to hold 10% of their checkable deposits as reserves, and in my example they also choose to keep an extra 10% of any new deposit as excess reserves because they are being cautious. Assume nobody changes how much cash they hold. After the money works its way through the whole banking system, how much will checkable deposits have increased in total? (Unit: dollar)

- 正确回答：5,000,000
- 检查：every given value appears in the text: True

**D1 缺前提**

> If the Fed buys bonds from the First National Bank, and an additional 10% of any deposit is held as excess reserves, the reserve requirement ratio is 10%.What is the total increase in checkable deposits? (Unit: dollar)

- 正确回答：算不出。缺：the amount of the Fed's bond purchase
- 检查：removed value absent from text: True

**D2 前提矛盾**

> The Fed buys $1 million of bonds from the First National Bank. The reserve requirement ratio is 10%, and banks hold an additional 10% of any deposit as excess reserves, so banks keep total reserves equal to 15% of their deposits.What is the total increase in checkable deposits? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：10% required plus 10% excess is 20% of deposits, not 15%
- 检查：contradiction verified by code: True

**D3 错误前提**

> The Fed buys $1 million of bonds from the First National Bank. The reserve requirement ratio is 10%, and banks hold an additional 10% of any deposit as excess reserves. Because banks hold excess reserves, the deposit multiplier is larger than it would be without them.What is the total increase in checkable deposits? (Unit: dollar)

- 正确回答：指出前提错误（excess reserves reduce the multiplier (1/(rr+e) = 5 instead of 10)），并给出正确值 5,000,000
- 检查：answer if the false premise is accepted: n/a

**D4 过时制度**

> It is November 2026. The Fed buys $1 million of bonds from the First National Bank. Under the Federal Reserve's current required reserve ratio of 10% on checkable deposits, and with banks holding an additional 10% of any deposit as excess reserves, what is the total increase in checkable deposits? (Unit: dollar)

- 正确回答：指出过时（Fed reserve requirement ratios have been 0% since 26 March 2020），按现行规则给出 10,000,000；照题中旧规则算是 5,000,000，判错
- 检查：stated-rule answer 5,000,000.0000 is 50.0% from current-rule answer

**D5 需说明假设**

> The Fed buys $1 million of bonds from the First National Bank. The reserve requirement ratio is 10%, and banks hold an additional 10% of any deposit as excess reserves. Some of the new deposits may be withdrawn by the public as cash.What is the total increase in checkable deposits? (Unit: dollar)

- 正确回答：写明关于「currency drain c (cash held per dollar of deposits); answer must equal 1,000,000/(0.20+c) for the stated c」的假设，数值与假设一致。可接受：no currency drain (c = 0) → 5,000,000；example c = 0.20 → 2,500,000
- 检查：options differ by 100.0%

## test_2758　FF

**O 原题**

> You decide to hold $100 less cash than usual and deposit $100 in cash in the bank. The rest of the public keeps its holdings of currency constant.If the reserve ratio (rr) is 5%, by how much will checkable deposits rise? (Unit: dollar)

- 正确回答：2,000

**E 加干扰信息**

> You decide to hold $100 less cash than usual and deposit $100 in cash in the bank. The rest of the public keeps its holdings of currency constant. Your checking account pays 0.5% interest, your bank has 12 branches, and the Fed pays 4.4% interest on reserve balances.If the reserve ratio (rr) is 5%, by how much will checkable deposits rise? (Unit: dollar)

- 正确回答：2,000
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> I usually keep a few hundred dollars in cash at home, partly out of habit from my parents. This month I decided to keep $100 less cash than usual and deposit that $100 into my checking account. In my economics class we are studying how deposits get multiplied through the banking system, and I want to apply it to my own little deposit. Assume that nobody else changes how much cash they hold (the rest of the public keeps its currency holdings constant), banks keep 5% of checkable deposits as reserves, and they lend out everything else. By how much will checkable deposits in the banking system rise in the end? (Unit: dollar)

- 正确回答：2,000
- 检查：every given value appears in the text: True

**D1 缺前提**

> You decide to hold $100 less cash than usual and deposit $100 in cash in the bank. The rest of the public keeps its holdings of currency constant.By how much will checkable deposits rise? (Unit: dollar)

- 正确回答：算不出。缺：the reserve ratio
- 检查：removed value absent from text: True

**D2 前提矛盾**

> You decide to hold $100 less cash than usual and deposit $100 in cash in the bank. The rest of the public keeps its holdings of currency constant. The reserve ratio is 5%, so for each $100 of deposits the bank must hold $10 in reserves.By how much will checkable deposits rise? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：5% of $100 is $5, not $10
- 检查：contradiction verified by code: True

**D3 错误前提**

> You decide to hold $100 less cash than usual and deposit $100 in cash in the bank. The rest of the public keeps its holdings of currency constant, and the reserve ratio is 5%. Since you only moved $100 from your pocket into the bank, checkable deposits in the banking system cannot rise by more than $100.By how much will checkable deposits rise? (Unit: dollar)

- 正确回答：指出前提错误（the new reserves support multiple deposit creation (1/0.05 = 20 times)），并给出正确值 2,000
- 检查：answer if the false premise is accepted: 100.0000 (95.0% off)

**D4 过时制度**

> It is November 2026. You decide to hold $100 less cash than usual and deposit $100 in cash in the bank. The rest of the public keeps its holdings of currency constant. Banks hold excess reserves equal to 2% of deposits, in addition to the Federal Reserve's current required reserve ratio of 5% on checkable deposits.By how much will checkable deposits rise? (Unit: dollar)

- 正确回答：指出过时（Fed reserve requirement ratios have been 0% since 26 March 2020），按现行规则给出 5,000；照题中旧规则算是 1,428.5714，判错
- 检查：stated-rule answer 1,428.5714 is 71.4% from current-rule answer

**D5 需说明假设**

> You decide to hold $100 less cash than usual and deposit $100 in cash in the bank. The rest of the public keeps its holdings of currency constant, and the required reserve ratio is 5%. Banks may also hold some excess reserves.By how much will checkable deposits rise? (Unit: dollar)

- 正确回答：写明关于「excess reserve ratio e; answer must equal 100/(0.05+e) for the stated e」的假设，数值与假设一致。可接受：no excess reserves (e = 0) → 2,000；example e = 0.05 → 1,000
- 检查：options differ by 100.0%

## test_171　NM

**O 原题**

> Cookie Dough Manufacturing has a target debt-equity ratio of 0.80. Its cost of equity is 17 percent, and its cost of debt is 10 percent. The tax rate is 35 percent.What is the company's WACC? (Unit: decimal)

- 正确回答：0.1233

**E 加干扰信息**

> Cookie Dough Manufacturing has a target debt-equity ratio of 0.80. Its cost of equity is 17 percent, and its cost of debt is 10 percent. The tax rate is 35 percent. The company's stock beta is 1.25, the market risk premium is 7 percent, its bonds carry an 8 percent coupon, and it has 2 million shares outstanding.What is the company's WACC? (Unit: decimal)

- 正确回答：0.1233
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> I just joined Cookie Dough Manufacturing as a junior analyst, and my first assignment is to update the discount rate we use for new oven lines. My manager is on vacation, so I am piecing things together from old files. Our CFO targets a debt-to-equity ratio of 0.80. Our cost of equity is 17 percent, and our pre-tax cost of debt is 10 percent. The tax rate we use in planning is 35 percent. I want to make sure I weight things correctly, because last year's file seems to have used the debt-to-equity ratio directly as the debt weight. What WACC should I use? (Unit: decimal)

- 正确回答：0.1233
- 检查：every given value appears in the text: True

**D1 缺前提**

> Cookie Dough Manufacturing's cost of equity is 17 percent, and its cost of debt is 10 percent. The tax rate is 35 percent.What is the company's WACC? (Unit: decimal)

- 正确回答：算不出。缺：the capital structure weights (target debt-equity ratio)
- 检查：removed value absent from text: True

**D2 前提矛盾**

> Cookie Dough Manufacturing has a target debt-equity ratio of 0.80, meaning that debt makes up 80 percent of its total capital. Its cost of equity is 17 percent, and its cost of debt is 10 percent. The tax rate is 35 percent.What is the company's WACC? (Unit: decimal)

- 正确回答：指出矛盾，不给数。矛盾：a D/E of 0.80 means debt is 0.8/1.8 = 44.4% of capital, not 80%
- 检查：contradiction verified by code: True

**D3 错误前提**

> Cookie Dough Manufacturing has a target debt-equity ratio of 0.80. Its cost of equity is 17 percent, and its cost of debt is 10 percent. The tax rate is 35 percent. Since both interest and dividends are tax-deductible, both the cost of debt and the cost of equity should be adjusted for taxes.What is the company's WACC? (Unit: decimal)

- 正确回答：指出前提错误（dividends are not tax-deductible; only the cost of debt is tax-adjusted），并给出正确值 0.1233
- 检查：answer if the false premise is accepted: 0.0903 (26.8% off)

**D4 过时制度**

> It is November 2026. Cookie Dough Manufacturing has a target debt-equity ratio of 0.80. Its cost of equity is 17 percent, and its pre-tax cost of debt is 10 percent. The company pays the current U.S. federal statutory corporate income tax rate of 35 percent; ignore state taxes.What is the company's WACC? (Unit: decimal)

- 正确回答：指出过时（the federal corporate rate has been a flat 21% since 2018 (TCJA), not 35%），按现行规则给出 0.1296；照题中旧规则算是 0.1233，判错
- 检查：stated-rule answer 0.1233 is 4.8% from current-rule answer

**D5 需说明假设**

> Cookie Dough Manufacturing has a target debt-equity ratio of 0.80. Its cost of equity is 17 percent. The financing desk reports a cost of debt of 10 percent but does not say whether this is before or after taxes. The tax rate is 35 percent.What is the company's WACC? (Unit: decimal)

- 正确回答：写明关于「whether the 10% cost of debt is pre-tax or after-tax」的假设，数值与假设一致。可接受：10% is pre-tax → 0.1233；10% is already after-tax → 0.1389
- 检查：options differ by 12.6%

## test_701　NM

**O 原题**

> Mullineaux Corporation has a target capital structure of 50 percent common stock, 5 percent preferred stock, and 45 percent debt. Its cost of equity is 15 percent, the cost of preferred stock is 6 percent, and the cost of debt is 8 percent. The relevant tax rate is 35 percent.What is Mullineaux's WACC? (Unit: decimal)

- 正确回答：0.1014

**E 加干扰信息**

> Mullineaux Corporation has a target capital structure of 50 percent common stock, 5 percent preferred stock, and 45 percent debt. Its cost of equity is 15 percent, the cost of preferred stock is 6 percent, and the cost of debt is 8 percent. The relevant tax rate is 35 percent. Its common stock trades at $45 with a beta of 1.2, its preferred pays a $6 dividend, and the company was founded in 1962.What is Mullineaux's WACC? (Unit: decimal)

- 正确回答：0.1014
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> My sister is doing an MBA and asked me to double-check a case she is working on, since I work in corporate finance. The case company is Mullineaux Corporation. Its target capital structure is 50 percent common stock, 5 percent preferred stock, and 45 percent debt. The case gives a cost of equity of 15 percent, a cost of preferred stock of 6 percent, and a pre-tax cost of debt of 8 percent, with a tax rate of 35 percent. She got a number that looks too low to her, and she is not sure whether the preferred stock should get a tax adjustment like the debt does. What is Mullineaux's WACC? (Unit: decimal)

- 正确回答：0.1014
- 检查：every given value appears in the text: True

**D1 缺前提**

> Mullineaux Corporation has a target capital structure of 50 percent common stock, 5 percent preferred stock, and 45 percent debt. Its cost of equity is 15 percent, the cost of preferred stock is 6 percent, and the pre-tax cost of debt is 8 percent.What is Mullineaux's WACC? (Unit: decimal)

- 正确回答：算不出。缺：the tax rate (needed for the after-tax cost of debt)
- 检查：removed value absent from text: True

**D2 前提矛盾**

> Mullineaux Corporation has a target capital structure of 50 percent common stock, 5 percent preferred stock, and 55 percent debt. Its cost of equity is 15 percent, the cost of preferred stock is 6 percent, and the cost of debt is 8 percent. The relevant tax rate is 35 percent.What is Mullineaux's WACC? (Unit: decimal)

- 正确回答：指出矛盾，不给数。矛盾：the weights add up to 110%
- 检查：contradiction verified by code: True

**D3 错误前提**

> Mullineaux Corporation has a target capital structure of 50 percent common stock, 5 percent preferred stock, and 45 percent debt. Its cost of equity is 15 percent, the cost of preferred stock is 6 percent, and the cost of debt is 8 percent. The relevant tax rate is 35 percent. Since preferred dividends are tax-deductible like interest, the cost of preferred stock should also be adjusted for taxes.What is Mullineaux's WACC? (Unit: decimal)

- 正确回答：指出前提错误（preferred dividends are not tax-deductible），并给出正确值 0.1014
- 检查：answer if the false premise is accepted: 0.1003 (1.0% off)

**D4 过时制度**

> It is November 2026. Mullineaux Corporation has a target capital structure of 50 percent common stock, 5 percent preferred stock, and 45 percent debt. Its cost of equity is 15 percent, the cost of preferred stock is 6 percent, and the pre-tax cost of debt is 8 percent. The company pays the current U.S. federal statutory corporate income tax rate of 35 percent; ignore state taxes.What is Mullineaux's WACC? (Unit: decimal)

- 正确回答：指出过时（the federal corporate rate has been a flat 21% since 2018 (TCJA), not 35%），按现行规则给出 0.1064；照题中旧规则算是 0.1014，判错
- 检查：stated-rule answer 0.1014 is 4.7% from current-rule answer

**D5 需说明假设**

> Mullineaux Corporation has a target capital structure of 50 percent common stock, 5 percent preferred stock, and 45 percent debt. Its cost of equity is 15 percent, the cost of preferred stock is 6 percent, and the pre-tax cost of debt is 8 percent. Its marginal tax rate is either the 21 percent federal rate alone or about 25 percent including state taxes; the case materials do not say which applies.What is Mullineaux's WACC? (Unit: decimal)

- 正确回答：写明关于「which tax rate applies」的假设，数值与假设一致。可接受：21% (federal only) → 0.1064；25% (federal and state) → 0.105
- 检查：options differ by 1.4%

## test_2281　NM

**O 原题**

> Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt, and its cost of equity is 16 percent. The firm can borrow at 9 percent. The corporate tax rate is 35 percent.What will the value of the firm be if Old School converts to 50 percent debt? (Unit: dollar)

- 正确回答：57,281.25

**E 加干扰信息**

> Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt, and its cost of equity is 16 percent. The firm can borrow at 9 percent. The corporate tax rate is 35 percent. The firm has 10,000 shares outstanding, its EBIT last year was $11,200, and the industry average debt ratio is 40 percent.What will the value of the firm be if Old School borrows an amount equal to 50 percent of its current all-equity value and uses it to repurchase shares? (Unit: dollar)

- 正确回答：57,281.25（debt = 50% of the unlevered value, as in the XFinBench answer）
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> My family owns Old School Corporation, a small business that has been very steady. It earns $12,000 in EBIT every year, and we expect that to continue forever. We have never borrowed. Investors in a business like ours would require 16 percent on the equity, and our bank says we can borrow at 9 percent. We pay corporate tax at 35 percent. The banker suggests we borrow an amount equal to half of what the company is worth today as an all-equity firm, use it to buy back some of my cousins' shares, and keep that debt in place permanently. My aunt thinks borrowing can only make the company worth less. If we follow the banker's plan, what would the company be worth? (Unit: dollar)

- 正确回答：57,281.25
- 检查：every given value appears in the text: True

**D1 缺前提**

> Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt. The firm can borrow at 9 percent. The corporate tax rate is 35 percent.What will the value of the firm be if Old School borrows an amount equal to 50 percent of its current all-equity value? (Unit: dollar)

- 正确回答：算不出。缺：the unlevered cost of equity (needed to value the all-equity firm)
- 检查：removed value absent from text: True

**D2 前提矛盾**

> Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt, its cost of equity is 16 percent, and its current all-equity value is $60,000. The firm can borrow at 9 percent. The corporate tax rate is 35 percent.What will the value of the firm be if Old School borrows an amount equal to 50 percent of its current all-equity value? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：12,000 x 0.65 / 0.16 = 48,750, not 60,000
- 检查：contradiction verified by code: True

**D3 错误前提**

> Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt, and its cost of equity is 16 percent. The firm can borrow at 9 percent. The corporate tax rate is 35 percent. Since interest tax shields have no value when debt is permanent, what will the value of the firm be if Old School borrows an amount equal to 50 percent of its current all-equity value? (Unit: dollar)

- 正确回答：指出前提错误（with corporate taxes, permanent debt adds T_c x D to firm value），并给出正确值 57,281.25
- 检查：answer if the false premise is accepted: 48,750.0000 (14.9% off)

**D4 过时制度**

> It is November 2026. Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt, and its cost of equity is 16 percent. The firm can borrow at 9 percent. It pays the current U.S. federal statutory corporate income tax rate of 35 percent; ignore state taxes.What will the value of the firm be if Old School borrows an amount equal to 50 percent of its current all-equity value? (Unit: dollar)

- 正确回答：指出过时（the federal corporate rate has been a flat 21% since 2018 (TCJA), not 35%），按现行规则给出 65,471.25；照题中旧规则算是 57,281.25，判错
- 检查：stated-rule answer 57,281.2500 is 12.5% from current-rule answer

**D5 需说明假设**

> Old School Corporation expects an EBIT of $12,000 every year forever. The firm currently has no debt, and its cost of equity is 16 percent. The firm can borrow at 9 percent. The corporate tax rate is 35 percent. Old School plans to borrow so that debt is 50 percent of the firm's value.What will the value of the firm be? (Unit: dollar)

- 正确回答：写明关于「50% of the current all-equity value or of the post-borrowing (levered) value」的假设，数值与假设一致。可接受：50% of all-equity value → 57,281.25；50% of levered value → 59,090.9091
- 检查：options differ by 3.2%

## test_2193　NM

**O 原题**

> Maxwell Industries has a corporate tax rate of 35 percent. Its unlevered cost of equity capital is 15.41 percent, and its cost of debt is 8 percent.What would the cost of equity be if the debt-equity ratio were 1.0? (Unit: decimal)

- 正确回答：0.2022

**E 加干扰信息**

> Maxwell Industries has a corporate tax rate of 35 percent. Its unlevered cost of equity capital is 15.41 percent, and its cost of debt is 8 percent. Maxwell's beta is 1.3, it has 5 million shares outstanding, and its existing bonds carry a 7 percent coupon.What would the cost of equity be if the debt-equity ratio were 1.0? (Unit: decimal)

- 正确回答：0.2023
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> I sit on the board of Maxwell Industries, and next week we are voting on a recapitalization. Management wants to issue permanent debt and buy back shares until the debt-equity ratio is 1.0. Several board members are worried that shareholders will demand a much higher return afterward. Here is what I have from the CFO's memo: our corporate tax rate is 35 percent, our unlevered cost of equity is 15.41 percent, and our cost of debt is 8 percent. I would like to walk into the meeting knowing the textbook answer. What would our cost of equity be at a debt-equity ratio of 1.0? (Unit: decimal)

- 正确回答：0.2023
- 检查：every given value appears in the text: True

**D1 缺前提**

> Maxwell Industries has a corporate tax rate of 35 percent, and its cost of debt is 8 percent.What would the cost of equity be if the debt-equity ratio were 1.0? (Unit: decimal)

- 正确回答：算不出。缺：the unlevered cost of equity (or of assets)
- 检查：removed value absent from text: True

**D2 前提矛盾**

> Maxwell Industries has a corporate tax rate of 35 percent. Its unlevered cost of equity capital is 15.41 percent, and its cost of debt is 8 percent.What would the cost of equity be if the debt-equity ratio were 1.0, so that debt makes up 75 percent of the firm's value? (Unit: decimal)

- 正确回答：指出矛盾，不给数。矛盾：a debt-equity ratio of 1.0 means debt is 50% of firm value, not 75%
- 检查：contradiction verified by code: True

**D3 错误前提**

> Maxwell Industries has a corporate tax rate of 35 percent. Its unlevered cost of equity capital is 15.41 percent, and its cost of debt is 8 percent. Since the interest tax shield offsets the extra risk, M&M Proposition II with taxes says the cost of equity does not change with leverage.What would the cost of equity be if the debt-equity ratio were 1.0? (Unit: decimal)

- 正确回答：指出前提错误（Proposition II with taxes: R_E = R_U + (R_U - R_D)(D/E)(1 - T_C), so R_E rises），并给出正确值 0.2023
- 检查：answer if the false premise is accepted: 0.1541 (23.8% off)

**D4 过时制度**

> It is November 2026. Maxwell Industries pays the current U.S. federal statutory corporate income tax rate of 35 percent; ignore state taxes. Its unlevered cost of equity capital is 15.41 percent, and its cost of debt is 8 percent.What would the cost of equity be if the debt-equity ratio were 1.0, with the debt kept permanently? (Unit: decimal)

- 正确回答：指出过时（the federal corporate rate has been a flat 21% since 2018 (TCJA), not 35%），按现行规则给出 0.2126；照题中旧规则算是 0.2023，判错
- 检查：stated-rule answer 0.2023 is 4.9% from current-rule answer

**D5 需说明假设**

> Maxwell Industries has a corporate tax rate of 35 percent. Its unlevered cost of equity capital is 15.41 percent, and its cost of debt is 8 percent. The company has not decided whether it will keep the dollar amount of debt fixed or rebalance its debt to keep the ratio constant.What would the cost of equity be if the debt-equity ratio were 1.0? (Unit: decimal)

- 正确回答：写明关于「debt policy」的假设，数值与假设一致。可接受：fixed (permanent) debt: R_U + (R_U - R_D)(D/E)(1 - T) → 0.2023；debt rebalanced to a constant ratio: R_U + (R_U - R_D)(D/E) → 0.2282
- 检查：options differ by 12.8%

## test_1506　NM; SP

**O 原题**

> Kolby Corp. is comparing two different capital structures, Plan I and Plan II. Plan I would result in 1,500 shares of stock and $20,000 in debt, while Plan II would result in 1,100 shares of stock and $30,000 in debt. The interest rate on the debt is 10 percent. The all-equity plan would result in 2,300 shares of stock outstanding.Ignoring taxes, when will EPS be identical for Plans I and II? (Unit: dollar)

- 正确回答：5,750

**E 加干扰信息**

> Kolby Corp. is comparing two different capital structures, Plan I and Plan II. Plan I would result in 1,500 shares of stock and $20,000 in debt, while Plan II would result in 1,100 shares of stock and $30,000 in debt. The interest rate on the debt is 10 percent. Kolby's stock price is $25, last year's EBIT was $6,400, and the firm's credit rating is BBB.Ignoring taxes, when will EPS be identical for Plans I and II? (Unit: dollar)

- 正确回答：5,750
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> I run Kolby Corp., a small manufacturing company, and our accountant has given me two ways to restructure our financing. Under Plan I we would have 1,500 shares outstanding and $20,000 of debt. Under Plan II we would have 1,100 shares outstanding and $30,000 of debt. Either way the bank charges 10 percent interest. We are a pass-through for now, so please ignore taxes. Our EBIT bounces around a lot from year to year depending on a couple of big customers, so I want to know the level of EBIT at which it would not matter to shareholders which plan we picked. At what EBIT would EPS be the same under both plans? (Unit: dollar)

- 正确回答：5,750
- 检查：every given value appears in the text: True

**D1 缺前提**

> Kolby Corp. is comparing two different capital structures, Plan I and Plan II. Plan I would result in 1,500 shares of stock and $20,000 in debt, while Plan II would result in 1,100 shares of stock and $30,000 in debt.Ignoring taxes, when will EPS be identical for Plans I and II? (Unit: dollar)

- 正确回答：算不出。缺：the interest rate on the debt
- 检查：removed value absent from text: True

**D2 前提矛盾**

> Kolby Corp. is comparing two capital structures. The all-equity plan would have 2,300 shares outstanding. Plan I would result in 1,500 shares of stock and $20,000 in debt, and Plan II in 1,100 shares of stock and $30,000 in debt, with the debt proceeds used to repurchase shares at $20 per share. The interest rate on the debt is 10 percent.Ignoring taxes, when will EPS be identical for Plans I and II? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：at $20 per share, $20,000 buys back 1,000 shares (leaving 1,300, not 1,500) and $30,000 buys back 1,500 (leaving 800, not 1,100); the share counts imply a $25 price
- 检查：contradiction verified by code: True

**D3 错误前提**

> Kolby Corp. is comparing two different capital structures, Plan I and Plan II. Plan I would result in 1,500 shares of stock and $20,000 in debt, while Plan II would result in 1,100 shares of stock and $30,000 in debt. The interest rate on the debt is 10 percent. Since Plan II uses more debt, its EPS is higher than Plan I's at every level of EBIT.Ignoring taxes, when will EPS be identical for Plans I and II? (Unit: dollar)

- 正确回答：指出前提错误（leverage raises EPS only above the break-even EBIT; below it Plan II has lower EPS），并给出正确值 5,750
- 检查：answer if the false premise is accepted: n/a

**D4 过时制度**

> It is November 2026. Kolby Corp. is considering Plan II, which would result in 1,100 shares of stock and $30,000 in debt at an interest rate of 10 percent. Kolby pays the current U.S. federal statutory corporate income tax rate of 35 percent; ignore state taxes.What is EPS under Plan II if EBIT is $8,000? (Unit: dollar)

- 正确回答：指出过时（the federal corporate rate has been a flat 21% since 2018 (TCJA), not 35%），按现行规则给出 3.5909；照题中旧规则算是 2.9545，判错
- 检查：stated-rule answer 2.9545 is 17.7% from current-rule answer

**D5 需说明假设**

> Kolby Corp. is comparing two different capital structures, Plan I and Plan II. Plan I would result in 1,500 shares of stock and $20,000 in debt at 10 percent interest. Plan II would result in 1,100 shares of stock and $30,000 in debt; its lender has quoted 10 percent but may raise the rate to 12 percent because of the higher leverage.Ignoring taxes, when will EPS be identical for Plans I and II? (Unit: dollar)

- 正确回答：写明关于「Plan II's interest rate」的假设，数值与假设一致。可接受：Plan II at 10% → 5,750；Plan II at 12% → 8,000
- 检查：options differ by 39.1%

## test_2972　NM; TR

**O 原题**

> You purchase a bond with a coupon rate of 7.5 percent and a clean price of $865. The next semiannual coupon payment is due in three months.What is the invoice price of the bond? (Unit: dollar)

- 正确回答：883.75

**E 加干扰信息**

> You purchase a bond with a coupon rate of 7.5 percent and a clean price of $865. The next semiannual coupon payment is due in three months. The bond was issued at par five years ago, it is callable, and the issuer's stock is up 8 percent this year.What is the invoice price of the bond? (Unit: dollar)

- 正确回答：883.75
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> I am buying my first individual corporate bond through my brokerage account, and the order screen shows two different prices, which is confusing me. The bond has a $1,000 face value and pays a 7.5 percent coupon, twice a year. The quoted clean price is $865. The next coupon payment is due in three months. The customer service person said something about accrued interest being added, but she could not tell me how much. How much will I actually pay for one bond, including accrued interest? (Unit: dollar)

- 正确回答：883.75
- 检查：every given value appears in the text: True

**D1 缺前提**

> You purchase a bond with a coupon rate of 7.5 percent, paid semiannually, and a clean price of $865.What is the invoice price of the bond? (Unit: dollar)

- 正确回答：算不出。缺：the time since the last coupon (or until the next coupon)
- 检查：removed value absent from text: True

**D2 前提矛盾**

> You purchase a bond with a coupon rate of 7.5 percent and a clean price of $865. The next semiannual coupon payment is due in three months, and the accrued interest is $25.What is the invoice price of the bond? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：halfway through a $37.50 coupon period the accrued interest is $18.75, not $25
- 检查：contradiction verified by code: True

**D3 错误前提**

> You purchase a bond with a coupon rate of 7.5 percent and a clean price of $865. The next semiannual coupon payment is due in three months. Since the quoted clean price already includes accrued interest, what is the invoice price of the bond? (Unit: dollar)

- 正确回答：指出前提错误（the clean price excludes accrued interest; invoice = clean + accrued），并给出正确值 883.75
- 检查：answer if the false premise is accepted: 865.0000 (2.1% off)

**D4 过时制度**

> It is Monday, August 3, 2026. You buy a U.S. corporate bond with a $1,000 face value and a 7.5 percent coupon paid semiannually on May 15 and November 15, at a clean price of $865. The trade settles on the standard T+2 settlement cycle for U.S. corporate bonds.How much accrued interest will you pay at settlement? (Unit: dollar)

- 正确回答：指出过时（U.S. corporate bonds settle T+1 since 28 May 2024 (settlement Tue Aug 4, not Wed Aug 5)），按现行规则给出 16.4583；照题中旧规则算是 16.6667，判错
- 检查：stated-rule answer 16.6667 is 1.3% from current-rule answer

**D5 需说明假设**

> You purchase a bond with a coupon rate of 7.5 percent and a clean price of $865. The next coupon payment is due in three months.What is the invoice price of the bond? (Unit: dollar)

- 正确回答：写明关于「coupon frequency」的假设，数值与假设一致。可接受：semiannual → 883.75；annual → 921.25
- 检查：options differ by 4.2%

## test_1405　TR

**O 原题**

> The Jackson-Timberlake Wardrobe Co. just paid a dividend of $1.60 per share on its stock. The dividends are expected to grow at a constant rate of 6 percent per year indefinitely. Investors require a 12 percent return on The Jackson-Timberlake Wardrobe Co. stock.What is the current price of The Jackson-Timberlake Wardrobe Co. stock? (Unit: dollar)

- 正确回答：28.27

**E 加干扰信息**

> The Jackson-Timberlake Wardrobe Co. just paid a dividend of $1.60 per share on its stock. The dividends are expected to grow at a constant rate of 6 percent per year indefinitely. The company's earnings per share are $3.20, its payout ratio is 50 percent, and its stock traded at $31 a year ago. Investors require a 12 percent return on The Jackson-Timberlake Wardrobe Co. stock.What is the current price of The Jackson-Timberlake Wardrobe Co. stock? (Unit: dollar)

- 正确回答：28.2667
- 检查：answer unchanged and no distractor equals it: True

**F 长段咨询**

> I have been reading about dividend investing and I am thinking about buying shares of The Jackson-Timberlake Wardrobe Co., a clothing company that has been around for decades. It just paid a dividend of $1.60 a share. Looking at its history and its business, I am comfortable assuming the dividend will keep growing at about 6 percent a year indefinitely. For a stock like this I would want a 12 percent return, since I could earn a decent amount on safer investments. I do not want to overpay just because the brand is familiar. Based on those assumptions, what is a fair price for one share today? (Unit: dollar)

- 正确回答：28.2667
- 检查：every given value appears in the text: True

**D1 缺前提**

> The Jackson-Timberlake Wardrobe Co. just paid a dividend of $1.60 per share on its stock. Investors require a 12 percent return on the stock.What is the current price of The Jackson-Timberlake Wardrobe Co. stock? (Unit: dollar)

- 正确回答：算不出。缺：the dividend growth rate
- 检查：removed value absent from text: True

**D2 前提矛盾**

> The Jackson-Timberlake Wardrobe Co. just paid a dividend of $1.60 per share on its stock. The dividends are expected to grow at a constant rate of 13 percent per year indefinitely. Investors require a 12 percent return on the stock.What is the current price of The Jackson-Timberlake Wardrobe Co. stock? (Unit: dollar)

- 正确回答：指出矛盾，不给数。矛盾：a perpetual growth rate (13%) at or above the required return (12%) has no finite value; the constant-growth model does not apply
- 检查：contradiction verified by code: True

**D3 错误前提**

> The Jackson-Timberlake Wardrobe Co. just paid a dividend of $1.60 per share on its stock. The dividends are expected to grow at a constant rate of 6 percent per year indefinitely, and investors require a 12 percent return. Since the dividend just paid is the one that drives the price, the price equals $1.60 divided by (12% - 6%).What is the current price of The Jackson-Timberlake Wardrobe Co. stock? (Unit: dollar)

- 正确回答：指出前提错误（the model uses next year's dividend D1 = 1.60 x 1.06），并给出正确值 28.2667
- 检查：answer if the false premise is accepted: 26.6667 (5.7% off)

**D4 过时制度**

> It is November 2026. The Jackson-Timberlake Wardrobe Co. just paid a dividend of $1.60 per share, and dividends are expected to grow at 6 percent per year indefinitely. Investors require a return equal to the current 12-month USD LIBOR rate of 5 percent plus an equity premium of 7 percentage points.What is the current price of the stock? (Unit: dollar)

- 正确回答：指出过时（USD LIBOR no longer exists），按现行规则给出 28.2667（只考指出，数值与题中规则下相同）
- 检查：flag only: the number is the same under the stated and current rules

**D5 需说明假设**

> The Jackson-Timberlake Wardrobe Co. pays a dividend of $1.60 per share on its stock. The dividends are expected to grow at a constant rate of 6 percent per year indefinitely. Investors require a 12 percent return on the stock.What is the current price of The Jackson-Timberlake Wardrobe Co. stock? (Unit: dollar)

- 正确回答：写明关于「whether $1.60 was just paid (D0) or is the next dividend (D1)」的假设，数值与假设一致。可接受：$1.60 just paid (D0) → 28.2667；$1.60 is next year's dividend (D1) → 26.6667
- 检查：options differ by 6.0%
