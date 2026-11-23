"""
Cohort model (in currency units, with real growth, no normalisation):
55 cohorts. Age 0..34: savers (pay in s*wage, reinvest share omega of dividends).
Age 35..54: retirees, sell at age a the fraction 1/(55-a) of their shares (everything at the end).
Fixed number of shares (=1). Price = total payment of buyers / total quantity of sellers.
Run: python3 cohorts.py
"""
import numpy as np
from scipy.optimize import brentq

g, pi, rho, omega, s = 0.035, 0.11, 0.55, 0.5, 0.027
NW, NR = 35, 20
N = NW + NR


def run(T=400, track_birth=250, g=g, pi=pi, rho=rho, omega=omega, s=s):
    h = np.zeros(N)
    h[NW:] = 1.0 / NR                         # start: all shares held by retirees
    P, Y, flows, log = [], [], [], []
    for t in range(T):
        Yt = (1 + g) ** t
        d = rho * pi * Yt                      # dividend per share (total shares = 1)
        w = (1 - pi) * Yt / NW                 # wage per saver
        f = np.zeros(N); f[NW:] = 1.0 / (N - np.arange(NW, N))   # selling fraction
        sell = f * h
        spend = np.zeros(N)
        spend[:NW] = s * w + omega * h[:NW] * d
        Ssum, Bsum = sell.sum(), spend.sum()
        p = Bsum / Ssum
        # cash flow of the cohort born in year track_birth (age = t - track_birth)
        age = t - track_birth
        if 0 <= age < N:
            cf = -spend[age] + h[age] * d + sell[age] * p
            log.append((t, age, cf, h[age], spend[age], sell[age] * p, w))
        h = h + spend / p - sell
        assert abs(h.sum() - 1.0) < 1e-9, "shares not conserved"
        h = np.concatenate(([0.0], h[:-1]))   # everyone ages one year; oldest cohort leaves (h=0)
        P.append(p); Y.append(Yt)
        flows.append((Bsum / Yt, Ssum, d / p))
    return np.array(P), np.array(Y), np.array(flows), log


def irr(cfs):
    f = lambda r: sum(cf / (1 + r) ** k for k, cf in enumerate(cfs))
    return brentq(f, -0.5, 1.0, xtol=1e-14)


if __name__ == "__main__":
    # calibrate the saving rate so that V/Y matches the first model (about 2.38)
    s_cal = brentq(lambda x: (lambda P, Y, *_: P[-1] / Y[-1])(*run(T=300, s=x)) - 2.3804, 0.005, 0.2, xtol=1e-12)
    print(f"calibrated saving rate (share of wage): {s_cal:.4%}  (base pool model: 2.7 %)")
    P, Y, fl, log = run(T=400, s=s_cal)
    v = P / Y
    y = fl[250, 2]
    R_exact = (1 + g) * (1 + y) - 1
    print(f"V/Y after 100/250/399 years: {v[100]:.4f} / {v[250]:.4f} / {v[399]:.4f}")
    print(f"inflow x/Y: {fl[399,0]:.3%}; payout yield {y:.3%}; total return {R_exact:.3%}")
    cfs = [c[2] for c in log]
    r = irr(cfs)
    print(f"cohort internal rate of return: {r:.4%}  (expected (1+g)(1+y)-1 = {R_exact:.4%})")
    ret = [c for c in log if c[1] == NW][0]
    print(f"value of the shares at retirement: {ret[3]*P[ret[0]]/ret[6]:.2f} annual wages")
    tot_in = sum(c[4] for c in log[:NW]); tot_out = sum(c[5] for c in log[NW:])
    print(f"paid in {tot_in:.3f}, sale proceeds {tot_out:.3f}, ratio {tot_out/tot_in:.2f}")
    ok = abs(r - R_exact) < 1e-6 and abs(v[399] - v[300]) < 1e-5
    print("test (cohort return = market return, steady state converges):", ok)
