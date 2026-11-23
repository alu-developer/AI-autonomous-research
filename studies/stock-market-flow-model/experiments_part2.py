"""Part 2: further criteria, extensions, portfolio model, self-tests. Run: python3 experiments_part2.py"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dataclasses import replace
import model as M1
import model_ext as M2
import model_portfolio as MP

OUT = "results"
os.makedirs(OUT, exist_ok=True)
BLUE, ORANGE, AQUA, GRAY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b"
checks, res = [], {}


def check(name, ok, info=""):
    checks.append((name, bool(ok), info))
    print(("PASS " if ok else "FAIL ") + name, info)


p1 = M1.Params()
s1 = M1.steady_state(p1)
p2 = M2.P2()
s2 = M2.steady2(p2)

# ------------------------------------------------------------ regression: extension = base model
check("R1 P2 without extensions: steady state = model.py", abs(s2["v"] - s1["v"]) < 1e-9, f"{s2['v']:.6f}")
kc1 = M1.critical_kappa(p1)
kc2 = M2.critical(replace(p2, kappa=0.0), "kappa", 5.0)
check("R2 critical kappa equals model.py", abs(kc1 - kc2) < 1e-4, f"{kc1:.5f} vs {kc2:.5f}")
res["regression"] = dict(v=s2["v"], kappa_c=kc2)

# ------------------------------------------------------------ K9: concentration (permanent holders)
rows = []
for qp in (0.0, 0.1, 0.2, 0.3, 0.4):
    q = replace(p2, qp=qp)
    sq = M2.steady2(q)
    q_cal = replace(q, s0=M2.calibrate_s0(q, s1["v"]))        # keep valuation fixed at 2.38
    kc = M2.critical(replace(q_cal, kappa=0.0), "kappa", 5.0)
    xm, vm = M2.wall2(q_cal)
    rows.append(dict(qp=qp, v_same_saving_rate=sq["v"], s0_calibrated=q_cal.s0, kappa_critical=kc,
                     x_steady_state=M2.steady2(q_cal)["x"], v_wall=vm, distance_to_wall=vm / s1["v"]))
res["K9_concentration"] = rows
check("K9 calibration hits v=2.38",
      all(abs(M2.steady2(replace(replace(p2, qp=r['qp']), s0=r['s0_calibrated']))['v'] - s1['v']) < 1e-9 for r in rows))
check("K9 more permanent holders -> smaller critical kappa (more fragile)", rows[-1]["kappa_critical"] < rows[0]["kappa_critical"],
      f"{rows[0]['kappa_critical']:.4f} -> {rows[-1]['kappa_critical']:.4f}")

# ------------------------------------------------------------ credit / leverage
rows = []
base = replace(p2, chi=0.3, icred=0.05)
for m in (0.0, 0.02, 0.04, 0.06, 0.08):
    q = replace(base, m=m)
    q_cal = replace(q, s0=M2.calibrate_s0(q, s1["v"]))
    sr = M2.spectral2(q_cal)
    sq = M2.steady2(q_cal)
    rows.append(dict(m=m, s0_cal=q_cal.s0, spectral_radius=sr, credit_to_gdp=sq["l"],
                     net_credit_contribution_to_inflow=(p1.g - q.icred) * sq["l"] / (1 + p1.g)))
res["credit_margin"] = rows
check("L1 m=0 -> spectral radius < 1 (no leverage is stable)", rows[0]["spectral_radius"] < 1, f"{rows[0]['spectral_radius']:.3f}")
mc = {}
for chi in (0.1, 0.3, 0.6, 1.0):
    q = replace(base, chi=chi)
    f = lambda m: M2.spectral2(replace(q, m=m, s0=M2.calibrate_s0(replace(q, m=m), s1["v"]))) - 1
    if f(0.5) < 0:
        mc[chi] = None
    else:
        lo, hi = 0.0, 0.5
        for _ in range(50):
            mid = .5 * (lo + hi)
            lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
        mc[chi] = .5 * (lo + hi)
res["credit_critical_m"] = {str(k): v for k, v in mc.items()}
print("critical m per chi:", mc)
chi0 = 0.6
if mc[chi0] is not None:
    for fac in (0.7, 1.3):
        q = replace(base, chi=chi0, m=fac * mc[chi0])
        q = replace(q, s0=M2.calibrate_s0(q, s1["v"]))
        o = M2.simulate2(q, 400, perturb=0.01, floor=False)
        dev = np.abs(o["v"] - s1["v"])
        if fac < 1:
            check("L2 credit below critical m: perturbation decays", dev[-50:].max() < 1e-4, f"{dev[-50:].max():.1e}")
        else:
            o = M2.simulate2(q, 400, perturb=0.01, floor=True)
            dev = np.abs(o["v"] - s1["v"])
            check("L2 credit above critical m: perturbation grows / cycle", dev[-50:].max() > 0.3, f"{dev[-50:].max():.2f}")

# ------------------------------------------------------------ margin debt today vs. threshold (data comparison)
m_real = 1.5 / 72        # margin debt ~1.5 trn USD (June 2026) / market value ~72 trn USD
res["margin_today"] = dict(m_real=m_real, critical_per_chi=res["credit_critical_m"])
res["credit_contribution_sign"] = dict(g=p1.g, i_credit=0.05, sign="negative" if p1.g < 0.05 else "positive")

# ------------------------------------------------------------ portfolio model
pp = MP.PP()
check("P1 portfolio: steady state = v_star", abs(MP.steady_v(pp) - pp.v_star) < 1e-9)
b = MP.b0(pp)
v_ = MP.steady_v(pp)
th = MP.theta(pp, v_, MP.R_ref(pp))
check("P2 market clearing V = theta/(1-theta)*B", abs(v_ - th / (1 - th) * b) < 1e-9, f"theta={th:.3f}")
rho_p = MP.spectral_p(pp)
check("P3 without extrapolation (chi=0): stable", rho_p < 1, f"{rho_p:.3f}")
cc = MP.critical_chi(pp)
res["P_critical_chi"] = float(cc)
for f in (0.7, 1.3):
    if np.isfinite(cc):
        vs, Rs, ths = MP.simulate_p(replace(pp, chi=f * cc), 500, perturb=0.02)
        dev = np.abs(vs - pp.v_star)
        if f < 1:
            check("P4 chi < critical: decays", dev[-50:].max() < 1e-4, f"{dev[-50:].max():.1e}")
        else:
            check("P4 chi > critical: grows / cycle", dev[-50:].max() > 0.2, f"{dev[-50:].max():.2f}")
rows = []
for i in (0.03, 0.04, 0.0505, 0.06, 0.07):
    v_port = MP.steady_v(pp, i=i)
    r_req = i + (MP.R_ref(pp) - pp.i)          # fixed excess return demanded
    v_gordon = pp.rhopi / (r_req - pp.g)
    rows.append(dict(i=i, v_portfolio=v_port, v_gordon_fixed_ERP=v_gordon))
res["P_interest"] = rows
check("P5 higher rate -> lower valuation (both models)",
      rows[-1]["v_portfolio"] < rows[0]["v_portfolio"] and rows[-1]["v_gordon_fixed_ERP"] < rows[0]["v_gordon_fixed_ERP"])
rows = []
for beta in (0.0, 0.005, 0.01, 0.02):
    vs, Rs, ths = MP.simulate_p(replace(pp, beta=beta, a=8.0), 400)
    rows.append(dict(beta=beta, v_100=float(vs[99]), v_400=float(vs[-1]), theta_400=float(ths[-1])))
res["P_beta"] = rows
res["P_wall_thmax"] = dict(thmax=pp.thmax, v_max_at_b0=pp.thmax / (1 - pp.thmax) * b)

# ------------------------------------------------------------ K6: net payout, K7: profit share
yield_div = 0.0117
yield_bb = 1.2 / 72
iss_lo, iss_hi = 0.6 / 72, 0.75 / 72
net_lo, net_hi = yield_div + yield_bb - iss_hi, yield_div + yield_bb - iss_lo
res["K6"] = dict(div=yield_div, buyback=yield_bb, issuance=[iss_lo, iss_hi], net=[net_lo, net_hi],
                 condition_r_minus_g=[(0.06 - 0.04), (0.08 - 0.04)])
res["K7"] = dict(v_max_at_pi=[dict(pi=pi_, v_max=0.55 * pi_ / (0.06 - 0.035)) for pi_ in (0.11, 0.15, 0.20, 0.30)])
# ------------------------------------------------------------ author's proposal: cap on trades relative to money
Mrel = 0.7   # assumption (illustrative): money stock / GDP
x_max_1 = M1.wall(p1)[0]
res["author_model"] = dict(M_to_GDP_assumption=Mrel, x_max_to_GDP=x_max_1, c_equivalent=x_max_1 / Mrel,
                           v_max_at_c=[dict(c=c, v_max=c * Mrel * (p1.Tw + p1.Tr)) for c in (0.05, 0.1, 0.2)])
check("N1 author's cap is K2 with a different denominator: v_max = c*(M/Y)*H",
      abs(res["author_model"]["v_max_at_c"][0]["v_max"] - 0.05 * Mrel * 55) < 1e-12)

# ------------------------------------------------------------ output
with open(f"{OUT}/results_part2.json", "w") as fh:
    json.dump(res, fh, indent=1, ensure_ascii=False, default=float)
print("all tests passed:", all(c[1] for c in checks))


def style(ax, title, xl, yl):
    ax.set_title(title, loc="left", fontsize=10, color=INK)
    ax.set_xlabel(xl, fontsize=8); ax.set_ylabel(yl, fontsize=8)
    ax.grid(alpha=.25, lw=.6); ax.tick_params(labelsize=8)
    for s in ("top", "right"): ax.spines[s].set_visible(False)


fig, ax = plt.subplots(2, 2, figsize=(11, 7.5), constrained_layout=True)
a = ax[0, 0]
a.plot([r["qp"] for r in res["K9_concentration"]], [r["kappa_critical"] for r in res["K9_concentration"]], color=BLUE, lw=2, marker="o")
style(a, "K9  More permanent holders: smaller critical kappa", "share of shares held by permanent holders", "critical kappa (valuation fixed at 2.38)")
a = ax[0, 1]
for chi, c in ((0.3, BLUE), (0.6, ORANGE), (1.0, AQUA)):
    ms = np.linspace(0, 0.3, 31)
    sr = []
    for m in ms:
        q = replace(base, chi=chi, m=m)
        q = replace(q, s0=M2.calibrate_s0(q, s1["v"]))
        sr.append(M2.spectral2(q))
    a.plot(ms, sr, color=c, lw=1.8, label=f"credit adjustment chi={chi}")
a.axhline(1, color=INK, lw=1); a.axvline(m_real, color=GRAY, ls="--", lw=1); a.text(m_real + .003, 12, "today (margin/market ~ 2 %)", fontsize=7, color=GRAY)
style(a, "Credit: spectral radius > 1 = leverage spiral", "credit / market value (cap m)", "spectral radius"); a.legend(fontsize=7, frameon=False)
a = ax[1, 0]
a.plot([r["i"] for r in res["P_interest"]], [r["v_portfolio"] for r in res["P_interest"]], color=BLUE, lw=2, label="portfolio model (equity share reacts)")
a.plot([r["i"] for r in res["P_interest"]], [r["v_gordon_fixed_ERP"] for r in res["P_interest"]], color=ORANGE, lw=2, label="Gordon, fixed excess return")
style(a, "K8  Rates up, valuation down", "risk-free rate", "market value / GDP"); a.legend(fontsize=7, frameon=False)
a = ax[1, 1]
for f, c in ((0.7, BLUE), (1.3, ORANGE)):
    if np.isfinite(cc):
        vs, _, _ = MP.simulate_p(replace(pp, chi=f * cc), 300, perturb=0.02)
        a.plot(vs, color=c, lw=1.6, label=f"extrapolation chi = {f}x critical")
a.axhline(pp.v_star, color=GRAY, ls="--", lw=1)
style(a, "Portfolio model: feedback", "years", "market value / GDP"); a.legend(fontsize=7, frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.98))
fig.savefig(f"{OUT}/overview_part2.png", dpi=150)
print("figure saved")
