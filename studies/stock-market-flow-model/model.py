"""
Toy model: the stock market as a money-flow system (savers -> dissavers).

Idea
----
* A fixed number of shares (= 1 unit, no new issuance).
* Two "pools" of share owners:
    - savers (share Qw of the shares): keep paying in, retire at rate mu = 1/Tw
    - dissavers (share Qr): sell the fraction lam = 1/Tr of their shares per year to live on
* The price follows directly from the money balance:
        price * (shares sold) = net money inflow x
  so market value V = x / S, where S is the fraction of all shares sold per year by dissavers
  (1/S = mean holding time H).
* Everything is measured relative to GDP Y (v = V/Y), so the model can run arbitrarily long
  without numbers overflowing.

This is a self-built teaching model, NOT a description of reality.
"""
from dataclasses import dataclass, replace
import numpy as np


@dataclass(frozen=True)
class Params:
    g: float = 0.035      # nominal GDP growth (e.g. 1.5 % real + 2 % inflation)
    pi: float = 0.11      # profit share of GDP
    rho: float = 0.55     # share of profits paid to owners (dividends + net buybacks)
    omega: float = 0.5    # share of savers' dividends that is reinvested
    s0: float = 0.027     # share of labour income that flows net into stocks
    Tw: float = 35.0      # mean saving phase (years)
    Tr: float = 20.0      # mean dissaving phase (years)
    eps: float = 0.0      # price sensitivity of sellers (0 = sell a fixed quantity)
    vbar: float = 2.4     # reference valuation V/Y, only relevant if eps > 0
    kappa: float = 0.0    # response of the saving rate to excess return (feedback)
    smin: float = 0.0
    smax: float = 0.15
    rref: float = None    # reference return; None = steady-state return


def pools(p):
    mu, lam = 1.0 / p.Tw, 1.0 / p.Tr
    return lam / (lam + mu), mu / (lam + mu)      # Qw, Qr in steady state


def x_tilde(p, s, Qw):
    """Net money inflow into the stock market, relative to GDP."""
    return s * (1 - p.pi) + p.omega * p.rho * p.pi * Qw


def steady_state(p):
    """Steady state. For eps > 0 the split of shares between pools also shifts -> fixed point."""
    from scipy.optimize import brentq
    mu, lam0 = 1.0 / p.Tw, 1.0 / p.Tr

    def parts(v):
        lam = lam0 * (v / p.vbar) ** p.eps          # effective selling rate
        Qw = lam / (lam + mu)
        Qr = mu / (lam + mu)
        return lam, Qw, Qr

    def f(v):
        lam, Qw, Qr = parts(v)
        return v - x_tilde(p, p.s0, Qw) / (lam * Qr)

    v = brentq(f, 1e-3, 1e3, xtol=1e-14)
    lam, Qw, Qr = parts(v)
    x = x_tilde(p, p.s0, Qw)
    yld = p.rho * p.pi / v
    return dict(Qw=Qw, Qr=Qr, H=p.Tw + p.Tr, x=x, v=v, yield_=yld, R=p.g + yld, S=lam * Qr)


def price(p, x, Qr, lam):
    """Solve v * S(v) = x with S = min(Qr, lam*Qr*(v/vbar)^eps)."""
    v = (x * p.vbar ** p.eps / (lam * Qr)) ** (1.0 / (1.0 + p.eps))
    S = lam * Qr * (v / p.vbar) ** p.eps
    if S > Qr:
        S = Qr
        v = x / Qr
    return v, S


def step(p, Qw, v_prev, R_prev, rref, s0_mult=1.0, lam_mult=1.0):
    mu = 1.0 / p.Tw
    lam = min(1.0, lam_mult / p.Tr)
    Qr = 1.0 - Qw
    if R_prev is None:
        s = p.s0 * s0_mult
    else:
        s = float(np.clip(p.s0 * s0_mult + p.kappa * (R_prev - rref), p.smin, p.smax))
    x = x_tilde(p, s, Qw)
    v, S = price(p, x, Qr, lam)
    R = None if v_prev is None else v * (1 + p.g) / v_prev - 1 + p.rho * p.pi / v_prev
    Qw_new = Qw + S - mu * Qw
    return dict(v=v, S=S, R=R, s=s, x=x, Qw_new=Qw_new)


def simulate(p, T, Qw0=None, shock=None):
    ss = steady_state(p)
    rref = ss["R"] if p.rref is None else p.rref
    Qw = ss["Qw"] if Qw0 is None else Qw0
    keys = ["v", "S", "R", "s", "x", "Qw"]
    out = {k: np.full(T, np.nan) for k in keys}
    v_prev, R_prev = None, None
    for t in range(T):
        sm, lm = (1.0, 1.0) if shock is None else shock(t)
        r = step(p, Qw, v_prev, R_prev, rref, sm, lm)
        out["v"][t], out["S"][t], out["s"][t], out["x"][t], out["Qw"][t] = (
            r["v"], r["S"], r["s"], r["x"], Qw)
        if r["R"] is not None:
            out["R"][t] = r["R"]
        v_prev, R_prev, Qw = r["v"], r["R"], r["Qw_new"]
    return out


# ---------------------------------------------------------------- analytics
def jacobian(p, h=1e-6):
    """Jacobian of the yearly map (Qw, v_prev, R_prev) -> (Qw', v, R) at the steady state."""
    ss = steady_state(p)
    rref = ss["R"] if p.rref is None else p.rref

    def F(z):
        r = step(p, z[0], z[1], z[2], rref)
        return np.array([r["Qw_new"], r["v"], r["R"]])

    z0 = np.array([ss["Qw"], ss["v"], ss["R"]])
    assert np.allclose(F(z0), z0, atol=1e-10), "not a fixed point"
    J = np.zeros((3, 3))
    for i in range(3):
        d = np.zeros(3)
        d[i] = h
        J[:, i] = (F(z0 + d) - F(z0 - d)) / (2 * h)
    return J


def spectral_radius(p):
    return float(max(abs(np.linalg.eigvals(jacobian(p)))))


def critical_kappa(p, lo=0.0, hi=5.0):
    """Smallest kappa with spectral radius >= 1 (bisection)."""
    f = lambda k: spectral_radius(replace(p, kappa=k)) - 1.0
    if f(hi) < 0:
        return np.inf
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def loop_gain_approx(p):
    """Rule of thumb: kappa*(1-pi)/(x*(1+eps))."""
    ss = steady_state(p)
    return p.kappa * (1 - p.pi) / (ss["x"] * (1 + p.eps))


def wall(p, smax=None, omega_max=1.0):
    """Maximum possible market value/GDP at maximum inflow capacity (eps = 0)."""
    smax = p.smax if smax is None else smax
    Qw, _ = pools(p)
    x_max = smax * (1 - p.pi) + omega_max * p.rho * p.pi * Qw
    return x_max, x_max * (p.Tw + p.Tr)


def forced_return_path(p, r_req, v0, T):
    """Investors always demand return r_req: v_{t+1} = ((1+r)v - rho*pi)/(1+g)."""
    v = np.empty(T)
    v[0] = v0
    for t in range(T - 1):
        v[t + 1] = ((1 + r_req) * v[t] - p.rho * p.pi) / (1 + p.g)
    return v


def gordon_value(p, r_req):
    return p.rho * p.pi / (r_req - p.g)
