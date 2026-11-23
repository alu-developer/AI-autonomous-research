"""Experiments, self-tests and figures for model.py. Run: python3 experiments.py"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from model import *

OUT = "results"
os.makedirs(OUT, exist_ok=True)
BLUE, ORANGE, AQUA, GRAY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b"
p = Params()
ss = steady_state(p)
res = {"baseline": {k: float(v) for k, v in ss.items()}}
checks = []


def check(name, ok, info=""):
    checks.append((name, bool(ok), info))
    print(("PASS " if ok else "FAIL ") + name, info)


# ---------------------------------------------------------------- self-tests
o = simulate(p, 400)
check("steady state: simulation = formula v=x*H", abs(o["v"][-1] - ss["v"]) < 1e-9, f"v={o['v'][-1]:.4f}")
check("steady-state return = g + payout yield", abs(o["R"][-1] - ss["R"]) < 1e-9, f"R={o['R'][-1]:.4%}")
o2 = simulate(p, 300, Qw0=0.2)
check("shares conserved (Qw in [0,1])", np.all((o2["Qw"] >= 0) & (o2["Qw"] <= 1)))
Qw_, Qr_ = ss["Qw"], ss["Qr"]
D = p.rho * p.pi
C = (1 - p.s0) * (1 - p.pi) + (1 - p.omega) * D * Qw_ + (D * Qr_ + ss["x"])
I = (1 - p.rho) * p.pi
check("goods balance: consumption + investment = GDP", abs(C + I - 1) < 1e-12, f"{C + I:.12f}")

# ---------------------------------------------------------------- E1: to "infinity"
T_LONG = 200_000
e1 = {}
for eps in (0.0, 4.0):
    q = replace(p, eps=eps)
    s_ = steady_state(q)
    finals = []
    for Qw0 in (0.1, 0.5, 0.9):
        out = simulate(q, T_LONG, Qw0=Qw0)
        finals.append(dict(Qw0=Qw0, v_final=float(out["v"][-1]), R_final=float(out["R"][-1]),
                           v_formula=float(s_["v"])))
    e1[f"eps={eps}"] = finals
    check(f"E1 convergence after {T_LONG} years (eps={eps})",
          all(abs(f["v_final"] - f["v_formula"]) < 1e-9 for f in finals), f"v*={s_['v']:.4f}")
res["E1_long_run"] = e1

# ---------------------------------------------------------------- E2: forced return
x_max, v_max = wall(p)
res["wall"] = dict(x_max=x_max, v_max=v_max)
e2 = {}
for r_req in (0.060, 0.065, 0.070):
    vg = gordon_value(p, r_req)
    path = forced_return_path(p, r_req, ss["v"], 3000)
    hit = np.where(path > v_max)[0]
    e2[f"r={r_req:.3f}"] = dict(v_gordon=float(vg), v0=float(ss["v"]),
                                 years_to_wall=int(hit[0]) if len(hit) else None,
                                 trend="grows" if ss["v"] > vg else "falls")
res["E2_forced_return"] = e2
check("E2 Gordon fixed point is unstable (multiplier (1+r)/(1+g)>1)", (1 + 0.065) / (1 + p.g) > 1)

# ---------------------------------------------------------------- E3: feedback
kc = critical_kappa(p)
res["E3_kappa_critical"] = float(kc)
res["E3_loop_gain_rule_of_thumb_at_kc"] = float(loop_gain_approx(replace(p, kappa=kc)))
e3 = {}
for f in (0.5, 1.5):
    q = replace(p, kappa=f * kc)
    out = simulate(q, 600, Qw0=ss["Qw"] + 0.01)
    dev = np.abs(out["v"] - ss["v"])
    e3[f"{f}*kc"] = dict(kappa=float(f * kc), v_min=float(np.nanmin(out["v"])), v_max=float(np.nanmax(out["v"])),
                         dev_start=float(dev[:60].max()), dev_end=float(dev[-60:].max()))
    if f < 1:
        check("E3 below critical kappa: perturbation decays", dev[-60:].max() < 1e-6, f"{dev[-60:].max():.2e}")
    else:
        check("E3 above critical kappa: perturbation grows", dev[-60:].max() > 0.5, f"{dev[-60:].max():.2f}")
res["E3_simulation"] = e3
check("E3 rule of thumb close to numerical critical kappa (+-15 %)",
      abs(res["E3_loop_gain_rule_of_thumb_at_kc"] - 1) < 0.15, f"{res['E3_loop_gain_rule_of_thumb_at_kc']:.3f}")

# ---------------------------------------------------------------- E4: shocks
sh_s = lambda t: (0.5, 1.0) if 50 <= t < 55 else (1.0, 1.0)
sh_l = lambda t: (1.0, 2.0) if 50 <= t < 60 else (1.0, 1.0)
o_s, o_l = simulate(p, 200, shock=sh_s), simulate(p, 200, shock=sh_l)


def rec(o):
    d = np.abs(o["v"] / ss["v"] - 1)
    after = np.where(d[60:] < 0.01)[0]
    return dict(v_min=float(o["v"].min()), drop=float(1 - o["v"].min() / ss["v"]),
                R_min=float(np.nanmin(o["R"])), years_to_1pct=int(after[0] + 60 - 50) if len(after) else None)


res["E4_shock_saving_halved_5y"] = rec(o_s)
res["E4_shock_selling_wave_x2_10y"] = rec(o_l)

# ---------------------------------------------------------------- E5: wall sensitivity
rows = []
for (tw, tr) in ((35, 20), (40, 25), (30, 15)):
    for smax in (0.10, 0.15, 0.20):
        q = replace(p, Tw=tw, Tr=tr)
        s_ = steady_state(q)
        xm, vm = wall(q, smax=smax)
        row = dict(Tw=tw, Tr=tr, smax=smax, v_start=float(s_["v"]), v_wall=float(vm))
        for gap in (0.01, 0.02, 0.03):
            row[f"years_gap_{int(gap*100)}pct"] = float(np.log(vm / s_["v"]) / np.log(1 + gap))
        rows.append(row)
res["E5_wall_table"] = rows

# ---------------------------------------------------------------- output
with open(f"{OUT}/results.json", "w") as fh:
    json.dump(res, fh, indent=1, ensure_ascii=False)
print(json.dumps({k: res[k] for k in res if k != "E5_wall_table"}, indent=1, ensure_ascii=False))
print("all tests passed:", all(c[1] for c in checks))


# ---------------------------------------------------------------- figures
def style(ax, title, xl, yl):
    ax.set_title(title, loc="left", fontsize=10, color=INK)
    ax.set_xlabel(xl, fontsize=8); ax.set_ylabel(yl, fontsize=8)
    ax.grid(alpha=.25, lw=.6); ax.tick_params(labelsize=8)
    for s in ("top", "right"): ax.spines[s].set_visible(False)


fig, ax = plt.subplots(2, 2, figsize=(11, 7.5), constrained_layout=True)
a = ax[0, 0]
for Qw0, c in zip((0.1, 0.5, 0.9), (BLUE, ORANGE, AQUA)):
    out = simulate(p, 300, Qw0=Qw0)
    a.plot(out["v"], color=c, lw=1.8, label=f"start with {int(Qw0*100)} % of shares held by savers")
a.axhline(ss["v"], color=GRAY, ls="--", lw=1); a.text(200, ss["v"] + .05, f"steady state {ss['v']:.2f}", fontsize=8, color=GRAY)
style(a, "1  Market value/GDP converges to a fixed ratio", "years", "market value / GDP"); a.legend(fontsize=7, frameon=False)

a = ax[0, 1]
for r_req, c in ((0.060, BLUE), (0.065, ORANGE), (0.070, AQUA)):
    a.plot(np.maximum(forced_return_path(p, r_req, ss["v"], 400), 0), color=c, lw=1.8, label=f"investors demand {r_req:.1%}")
a.axhline(v_max, color=INK, lw=1); a.text(5, v_max + .15, f"inflow wall = {v_max:.1f}", fontsize=8)
a.set_ylim(0, 11)
style(a, "2  Fixed required return: the equilibrium is a knife edge", "years", "market value / GDP"); a.legend(fontsize=7, frameon=False, loc="center right")

a = ax[1, 0]
for f, c in ((0.5, BLUE), (1.5, ORANGE)):
    out = simulate(replace(p, kappa=f * kc), 300, Qw0=ss["Qw"] + 0.01)
    a.plot(out["v"], color=c, lw=1.6, label=f"response kappa = {f}x critical")
a.axhline(ss["v"], color=GRAY, ls="--", lw=1)
a.set_ylim(0, 11)
style(a, "3  Feedback: loop gain above 1 gives boom and bust", "years", "market value / GDP"); a.legend(fontsize=7, frameon=False, loc="upper right", ncol=2)

a = ax[1, 1]
a.plot(o_s["v"][:130], color=BLUE, lw=1.8, label="saving halved for 5 years")
a.plot(o_l["v"][:130], color=ORANGE, lw=1.8, label="selling wave x2 for 10 years")
a.axhline(ss["v"], color=GRAY, ls="--", lw=1)
style(a, "4  Shocks: price follows the inflow, then recovers", "years", "market value / GDP"); a.legend(fontsize=7, frameon=False)
fig.savefig(f"{OUT}/overview.png", dpi=150)
print("figure saved")
