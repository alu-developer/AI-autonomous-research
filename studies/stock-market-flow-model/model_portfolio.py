"""
Second, deliberately different model: portfolio / valuation model.
Households split wealth W = V + B between stocks (V) and bonds/deposits (B).
Equity share: theta = theta* + a * (expected excess return - excess return in the base state), clipped.
Market clearing: V = theta * (V + B)  ->  V = theta/(1-theta) * B.
Expected return = payout yield + expected growth (+ extrapolation of the last excess return, chi).
Everything relative to GDP. B/Y = b grows with GDP (plus optional over-growth beta, e.g. credit/money).
"""
from dataclasses import dataclass, replace
import numpy as np
from scipy.optimize import brentq


@dataclass(frozen=True)
class PP:
    g: float = 0.035
    rhopi: float = 0.0605        # payouts relative to GDP
    i: float = 0.0505            # risk-free rate (10-year US Treasury, 2026-11-19)
    v_star: float = 2.3804       # base valuation
    theta_star: float = 0.45     # equity share in the base state (assumption)
    a: float = 8.0               # response of equity share to expected excess return
    chi: float = 0.0             # extrapolation of the last excess return
    thmin: float = 0.0
    thmax: float = 0.95
    beta: float = 0.0            # over-growth of B relative to GDP


def b0(p):
    return p.v_star * (1 - p.theta_star) / p.theta_star


def R_ref(p):
    return p.g + p.rhopi / p.v_star


def theta(p, v, Rlag, i=None):
    i = p.i if i is None else i
    mu = p.rhopi / v + p.g + p.chi * (Rlag - R_ref(p))
    base = R_ref(p) - p.i                      # excess return in the base state
    return float(np.clip(p.theta_star + p.a * ((mu - i) - base), p.thmin, p.thmax))


def clear(p, b, Rlag, i=None):
    f = lambda v: v - theta(p, v, Rlag, i) * (v + b)
    return brentq(f, 1e-4, 1e4, xtol=1e-13)


def steady_v(p, i=None, b=None):
    return clear(p, b0(p) if b is None else b, R_ref(p), i)


def simulate_p(p, T, perturb=0.0):
    b = b0(p)
    v_prev, R_prev = p.v_star * (1 + perturb), R_ref(p)
    vs, Rs, ths = [], [], []
    for t in range(T):
        b *= (1 + p.beta)
        v = clear(p, b, R_prev)
        R = v * (1 + p.g) / v_prev - 1 + p.rhopi / v_prev
        vs.append(v); Rs.append(R); ths.append(v / (v + b))
        v_prev, R_prev = v, R
    return np.array(vs), np.array(Rs), np.array(ths)


def spectral_p(p, h=1e-6):
    b = b0(p)
    F = lambda z: (lambda v: np.array([v, v * (1 + p.g) / z[0] - 1 + p.rhopi / z[0]]))(clear(p, b, z[1]))
    z0 = np.array([p.v_star, R_ref(p)])
    assert np.allclose(F(z0), z0, atol=1e-9)
    J = np.zeros((2, 2))
    for k in range(2):
        d = np.zeros(2); d[k] = h
        J[:, k] = (F(z0 + d) - F(z0 - d)) / (2 * h)
    return float(max(abs(np.linalg.eigvals(J))))


def critical_chi(p, hi=20.0):
    f = lambda c: spectral_p(replace(p, chi=c)) - 1.0
    if f(hi) < 0:
        return np.inf
    lo = 0.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return 0.5 * (lo + hi)
