# Can the stock market keep growing forever? A money-flow toy model

Status: **exploratory toy study (2026-11-23). Not a preregistered run, not human-reviewed, not a research result.** It was done outside the `airesearch` pipeline at the author's request, for personal interest. All numbers are model assumptions chosen to resemble today's orders of magnitude (market value about 2.4 x GDP, return about 6 %). They were not fitted to data. Not investment advice. Real-world data points quoted in part 2 come from web searches in Nov 2026 and were **not** verified against primary sources (source URLs were not recorded; treat them as unverified).

## Question
If today's system is run for arbitrarily long, where does the stock market end up, how does money flow, and which conditions must hold permanently?

## The model in five sentences
1. A fixed number of shares. Owners are **savers** (pay in; mean saving phase $T_w=35$ years) and **dissavers** (sell to live on; mean dissaving phase $T_r=20$ years).
2. The price follows from the money balance: price $\times$ shares sold = net money inflow $x$.
3. Hence market value $V = x\cdot H$ (Little's law), with $H=T_w+T_r$ the mean holding time. Relative to GDP: $V/Y=(x/Y)\cdot H$.
4. Inflow $x/Y = s(1-\pi) + \omega\rho\pi Q_w$: saved labour income plus reinvested dividends of savers.
5. Return $R = g + \rho\pi/(V/Y)$: GDP growth plus payout yield.

Short-term trading between investors is left out (it nets to zero). Parameters are in `model.py`.

## Part 1: results (`results/results.json`, `results/overview.png`; run `python3 experiments.py`)

**1. Infinite horizon with constant structure: the market converges.** With constant saving rate, profit share, payout ratio and age structure, $V/Y$ converges from any start to a fixed value (here 2.38), tested up to 200,000 years (deviation from formula $<10^{-9}$), also with price-sensitive sellers. Return converges to $g+$ payout yield (6.04 %). In steady state 4.3 % of GDP flows net into the market per year (1.8 % of market value).

**2. A permanently fixed required return is a knife edge.** If investors always demand $r$, then $v_{t+1}=((1+r)v_t-\rho\pi)/(1+g)$. The fixed point $v^*=\rho\pi/(r-g)$ (Gordon value) is **unstable**: above it the gap grows by the factor $(1+r)/(1+g)$ per year. At $r=6.5\,\%$, $v^*=2.02$ and the inflow wall is reached after 106 years; at $r=7\,\%$ after 75 years.

**3. There is a hard wall: inflow capacity.** With at most 15 % of labour income saved and full reinvestment of dividends, $x_{max}/Y=17.2\,\%$, so $V/Y\le 9.5$. Years until the wall if $V/Y$ outgrows GDP by $\Delta$ per year: 1 % -> 139 (range 108-163), 2 % -> 70 (54-82), 3 % -> 47 (36-55). The wall depends only logarithmically on $s_{max}$.

**4. Feedback decides between stable and boom-bust.** If investors raise inflow after above-normal returns ($s_t=s_0+\kappa(R_{t-1}-R_{ref})$), there is a critical $\kappa_c\approx0.046$ (Jacobian; rule of thumb: loop gain $\kappa(1-\pi)/(x(1+\varepsilon))=1$). Below it perturbations decay; above it a permanent cycle appears. The value of $\kappa$ is an assumption; the existence of the threshold is the result.

**5. Shocks.** Saving halved for 5 years: market value -28 %. Selling wave (double selling rate, 10 years): -50 %, then about 55 years to come within 1 % of the steady state.

## Critical conditions (checklist)
| No. | Condition | Measurable as |
|---|---|---|
| K1 | Payouts carry the return | net payout yield (dividends + net buybacks - issuance) $\ge r-g$; equivalently $V/Y\le\rho\pi/(r-g)$ |
| K2 | Inflow below capacity | $V/Y=(x/Y)H\le (x/Y)_{max}H$ |
| K3 | Structural ratios bounded | saving rate, profit share, payout ratio, age structure without permanent trend |
| K4 | Loop gain $<1$ | response of net inflow to last year's return ($\kappa$) |
| K5 | Goods balance | consumption + investment = GDP (identity in the model, tested) |
| K6 | Net issuance | payout yield must be measured net of new issuance |
| K7 | Profit-share bound | $V/Y\le\rho\pi_{max}/(r-g)$ |
| K8 | Interest-rate sensitivity | valuation vs. risk-free rate |
| K9 | Ownership concentration | share of shares held by permanent holders |

## Part 2: are the assumptions met today? (`results/results_part2.json`, `results/overview_part2.png`; run `python3 experiments_part2.py`)
New files: `model_ext.py` (permanent holders, credit), `model_portfolio.py` (second, differently built model). Default values of `model_ext.py` reproduce part 1 exactly (tests R1, R2).

| Criterion | Data (Nov 2026, from web searches, unverified) | Verdict |
|---|---|---|
| K1 net payout | dividends 1.17 % + buybacks about 1.2 trn USD / 72 trn USD (1.7 %) - issuance about 0.6-0.75 trn USD (0.8-1.0 %): **net about 1.8-2.0 %** (own estimate) | borderline: enough for $r-g=2\,\%$, not for 4 % |
| risk premium | forward earnings yield about 5.65 % vs. 10-year Treasury 5.05 % | thin |
| K2 inflow capacity, K4 feedback | $s_{max}$ and $\kappa$ are assumed, never measured | **not testable** |
| K9 concentration | top 10 % hold about 88 %, top 1 % about 51 % (Fed DFA 2026Q2, partly extrapolated) | high |
| credit | margin debt about 1.5 trn USD (June 2026, record) = about 2.1 % of market value | see below |

**K7.** At $r=6\,\%$, $g=3.5\,\%$, $\rho=0.55$ the bound is 2.42 at $\pi=0.11$ (model today: 2.38, at the edge), 3.3 at $\pi=0.15$, 6.6 at $\pi=0.30$.
**K8.** Risk-free rate 5.05 % -> 7 %: $V/Y$ falls from 2.38 to 1.72 (portfolio model) or 1.35 (Gordon, fixed excess return). At 3 %: 3.5 or 12.3.
**K9.** At equal saving rate $V/Y$ rises with the share $q_p$ of permanent holders (0.2: 3.13; 0.4: 4.37). Holding $V/Y=2.38$ fixed, $\kappa_c$ falls from 0.046 ($q_p=0$) to 0.027 ($q_p=0.4$): more concentration makes feedback more dangerous.
**Credit.** Critical credit cap $m$ (leverage spiral) by credit adjustment speed $\chi$: 18.5 % ($\chi=0.1$), 6.2 % (0.3), 3.1 % (0.6), 1.85 % (1.0). Today about 2.1 %, so only with very fast credit adjustment is the threshold in reach; $\chi$ is not measured. The steady credit contribution $(g-i)\,l$ is **negative** while the credit rate (5 %) exceeds growth (3.5 %).

## Critique of the models
**Author's proposal** (cap on annual net trades as a share $c$ of the money stock $M$): mathematically the same as K2 with a different denominator, $V/Y\le c\,(M/Y)\,H$ (test N1). The idea of an inflow cap is right. Weak: money is a stock, the inflow is a flow of income; the same money can circulate several times a year, and $M$ also grows through credit. GDP/saving flow is the better denominator, and $M/Y$ is not constant. With the assumed $M/Y=0.7$ (unchecked): $c=5\,\%$ gives $V/Y\le1.9$, $10\,\%$ gives 3.85, $20\,\%$ gives 7.7, so everything hinges on an invented $c$.

**Weaknesses of the flow model:** no interest-rate channel (only in the portfolio model), fixed-quantity selling, exponential holding times, bequests/inequality only through $q_p$, $s_{max}$ invented, $\kappa$ and $\chi$ not measured.

**The two models disagree on one point.** In the portfolio model $V=\frac{\theta}{1-\theta}B$ is bound only to wealth and equity share. If $B/Y$ grows faster than GDP by $\beta$, $V/Y$ grows without an inflow wall, limited only by $\theta_{max}$ (at 95 %: $V/Y\le55$). With $\beta=1\,\%$, $V/Y$ is 4.4 after 100 years and 53 after 400. Whether credit/money creation can supply unlimited inflow is the main open question; neither model settles it.

## Part 3: cohort model (`cohorts.py`; run `python3 cohorts.py`)
Check of the individual-level story in currency units with real growth: 55 cohorts, each saves for 35 years, then sells over 20 years; the price follows from total inflow / total sales. With the saving rate calibrated to $V/Y=2.38$ (8.2 % of wage; differs from the pool model because the selling schedule differs, so levels are not reliable):
* $V/Y$ converges to 2.38;
* every cohort earns exactly the market return, 6.13 % per year ($=(1+g)(1+\text{yield})-1$; tested to $10^{-6}$), including compound interest;
* shares are worth about 3.6 annual wages at retirement; total sale proceeds are about 2.4 times total payments.
Why a factor 7.7 (35 years at 6 %) against 3.3 (35 years of 3.5 % income growth) is no problem: 7.7 applies only to the very first euro paid in; payments grow with wages, so most euros compound much shorter.

## Conclusions
1. In the model the market converges if K1-K4 hold permanently. K1 (payouts) or K7 (profit share) fail first, not the inflow wall.
2. Today K1 and K7 are borderline, K9 and credit are elevated, K2 and K4 cannot be measured.
3. These are toy-model statements, not a forecast.

## Honest limits
Not modelled: foreign capital, central bank purchases, bonds in the flow model, government, politics, taxes, fees. The feedback rule is invented, no empirical estimate of $\kappa$ or $\chi$ exists. Parameters are plausible magnitudes, not measurements. An earlier chat heuristic using the Gabaix-Koijen multiplier was crude and is superseded.

## Possible next step
Estimate $\kappa$ and $\chi$ from historical data, so that K4 and the credit threshold are tested rather than assumed; build a model with banks and money creation to address the open question above.

## Files
`model.py`, `experiments.py` (part 1, 10 self-tests, figure), `model_ext.py`, `model_portfolio.py`, `experiments_part2.py` (part 2, self-tests, figure), `cohorts.py` (part 3). Requirements: Python 3, numpy, scipy, matplotlib.
