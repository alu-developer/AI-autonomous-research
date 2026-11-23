"""
Extensions of the flow model (model.py is unchanged):
  qp     : share of all shares held by "permanent holders" (very wealthy) who never sell
  omega_p: share of permanent holders' dividends that is reinvested
  m      : credit cap (margin debt / market value); chi: adjustment speed of credit
  icred  : interest rate on credit (paid by investors out of their inflow)
Price formation as before: price = net inflow / shares sold (eps = 0).
"""
from dataclasses import dataclass, replace
import numpy as np
from model import Params


@dataclass(frozen=True)
class P2(Params):
    qp: float = 0.0
    omega_p: float = 0.5
    m: float = 0.0
    chi: float = 0.3
    icred: float = 0.05
    xfloor: float = 0.25     # lower bound of the inflow (share of steady-state inflow), simulation only


def _pools(p):
    mu, lam = 1 / p.Tw, 1 / p.Tr
    F = 1 - p.qp
    return F * lam / (lam + mu), F * mu / (lam + mu), mu, lam


def _x_base(p, s, Qw):
    return s * (1 - p.pi) + p.omega * p.rho * p.pi * Qw + p.omega_p * p.rho * p.pi * p.qp


def steady2(p):
    Qw, Qr, mu, lam = _pools(p)
    c = (p.g - p.icred) * p.m / (1 + p.g)
    xb = _x_base(p, p.s0, Qw)
    v = xb / (lam * Qr - c)
    l = p.m * v
    x = xb + c * v
    return dict(Qw=Qw, Qr=Qr, v=v, l=l, x=x, R=p.g + p.rho * p.pi / v, S=lam * Qr)


def calibrate_s0(p, v_target):
    """Choose the saving rate s0 so that the steady state equals v_target (may turn negative = implausible)."""
    Qw, Qr, mu, lam = _pools(p)
    c = (p.g - p.icred) * p.m / (1 + p.g)
    xb = v_target * (lam * Qr - c)
    rest = p.omega * p.rho * p.pi * Qw + p.omega_p * p.rho * p.pi * p.qp
    return (xb - rest) / (1 - p.pi)


def step2(p, z, rref, smult=1.0, lmult=1.0, floor=False, ss=None):
    Qw, l, v_prev, R_prev = z
    mu = 1 / p.Tw
    lam = min(1.0, lmult / p.Tr)
    F = 1 - p.qp
    Qr = F - Qw
    s = float(np.clip(p.s0 * smult + p.kappa * (R_prev - rref), p.smin, p.smax))
    d = p.chi * (p.m * v_prev - l) + p.g * l if p.m > 0 else 0.0   # credit flow, relative to Y_{t-1}
    x = _x_base(p, s, Qw) + (d - p.icred * l) / (1 + p.g)
    if floor:
        x = max(x, p.xfloor * ss["x"])
    v = x / (lam * Qr)
    S = lam * Qr
    R = v * (1 + p.g) / v_prev - 1 + p.rho * p.pi / v_prev
    l_new = (l + d) / (1 + p.g) if p.m > 0 else 0.0
    return (Qw + S - mu * Qw, l_new, v, R), dict(v=v, R=R, s=s, x=x, l=l_new)


def simulate2(p, T, shock=None, perturb=0.0, floor=True):
    ss = steady2(p)
    rref = ss["R"]
    z = (ss["Qw"] + perturb, ss["l"], ss["v"], ss["R"])
    out = {k: np.empty(T) for k in ("v", "R", "s", "x", "l")}
    for t in range(T):
        sm, lm = (1.0, 1.0) if shock is None else shock(t)
        z, o = step2(p, z, rref, sm, lm, floor=floor, ss=ss)
        for k in out:
            out[k][t] = o[k]
    return out


def spectral2(p, h=1e-6):
    ss = steady2(p)
    rref = ss["R"]
    F = lambda z: np.array(step2(p, tuple(z), rref)[0])
    z0 = np.array([ss["Qw"], ss["l"], ss["v"], ss["R"]])
    assert np.allclose(F(z0), z0, atol=1e-9), "not a fixed point"
    J = np.zeros((4, 4))
    for i in range(4):
        d = np.zeros(4); d[i] = h
        J[:, i] = (F(z0 + d) - F(z0 - d)) / (2 * h)
    return float(max(abs(np.linalg.eigvals(J))))


def critical(p, field, hi, lo=0.0):
    f = lambda x: spectral2(replace(p, **{field: x})) - 1.0
    if f(hi) < 0:
        return np.inf
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return 0.5 * (lo + hi)


def wall2(p, smax=None):
    smax = p.smax if smax is None else smax
    Qw, Qr, mu, lam = _pools(p)
    x_max = smax * (1 - p.pi) + p.rho * p.pi * (Qw + p.qp)      # all dividends reinvested
    return x_max, x_max / (lam * Qr)
