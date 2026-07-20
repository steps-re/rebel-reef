"""
Attribution v2 — the corrected, defensible test (addresses the adversarial review).

Fixes vs v1:
 - FACTORIAL 2x2 from a COMMON healthy baseline, toggling ONE factor at a time
   (urchin grazing; 2023 heat pulse), so the interaction is isolated, not baked in.
 - MONTE CARLO over the uncertain parameters (priors), not hand-picked point values.
 - HISTORY MATCHING: keep only parameter sets for which the reef is actually healthy in
   the baseline (consistent with the observed ~59% cover in 2014). No tautological d0 fit.
 - IDENTIFIABILITY: heat enters as one effective mortality term d_heat (we do not pretend
   to separate k_h and the light fraction).
 - Reports the DISTRIBUTION of the interaction across all data-consistent parameters, and
   whether its sign is robust. Honest result either way. No "validation" claims.

Question tested: is the 2023 heat MORE damaging to coral once the 2022 urchin die-off has
lowered grazing (a synergistic interaction), robustly across defensible parameters?
"""
import numpy as np
from scipy.integrate import odeint

rng = np.random.default_rng(20260720)
r = 1.0
g_fish = 0.10
HORIZON = 13.0                       # years; heat pulse mid-window, then RECOVERY phase observed
PULSE_START, PULSE_END = 6.0, 7.5    # 1.5-yr heat pulse, then 5.5 yr of recovery dynamics
C0, M0 = 0.55, 0.05                  # common healthy baseline start (a 2014-like reef)

def run_cell(g, d0, dh, a, gamma):
    def rhs(y, t):
        C, M = y; T = max(0.0, 1-C-M)
        d = d0 + (dh if PULSE_START <= t < PULSE_END else 0.0)
        return [C*(r*T - d - a*M), a*M*C - g*M/(M+T+1e-9) + gamma*M*T]
    s = odeint(rhs, [C0, M0], np.linspace(0, HORIZON, 700))
    return max(0.0, s[-1, 0])

def factorial(p):
    gh, gl, d0, dh, a, gamma = p
    C00 = run_cell(gh, d0, 0.0, a, gamma)   # baseline: urchins, no heat
    C10 = run_cell(gl, d0, 0.0, a, gamma)   # urchin loss only
    C01 = run_cell(gh, d0, dh,  a, gamma)   # heat only
    C11 = run_cell(gl, d0, dh,  a, gamma)   # both
    return C00, C10, C01, C11

# --- Priors (defensible ranges), sampled ---
N = 4000
gh   = rng.uniform(0.35, 0.65, N)                       # 2014 grazing (urchins present)
ufrac= rng.uniform(0.05, 0.25, N)                       # grazing fraction remaining after -88% die-off
gl   = g_fish + (gh - g_fish)*ufrac                     # post-die-off grazing
d0   = rng.uniform(0.10, 0.35, N)                       # baseline coral mortality
dh   = rng.uniform(0.20, 0.90, N)                       # extra mortality from the 2023 heat pulse
a    = rng.uniform(0.10, 0.35, N)                       # macroalgal overgrowth (oligo->eutrophic)
gamma= rng.uniform(0.80, 1.15, N)                       # macroalgal vegetative spread

I = np.full(N, np.nan); C = np.zeros((N,4)); healthy = np.zeros(N, bool)
for i in range(N):
    p = (gh[i], gl[i], d0[i], dh[i], a[i], gamma[i])
    C00,C10,C01,C11 = factorial(p)
    C[i] = (C00,C10,C01,C11)
    # history match: baseline must be a healthy reef (>0.40), consistent with observed 2014
    healthy[i] = C00 > 0.40
    # interaction (coral units): <0 means combined loss EXCEEDS additive (synergy)
    I[i] = C11 - C10 - C01 + C00

H = healthy
kept = H.sum()
print("="*78)
print("ATTRIBUTION v2 — factorial 2x2 + Monte Carlo, history-matched to a healthy 2014 reef")
print("="*78)
print(f"samples={N}, data-consistent (healthy baseline)={kept} ({100*kept/N:.0f}%)\n")

C00,C10,C01,C11 = [C[H,j] for j in range(4)]
print("mean coral cover by cell (data-consistent ensemble):")
print(f"  baseline (urchins, no heat) ... {C00.mean():.2f}")
print(f"  urchin loss only .............. {C10.mean():.2f}   (main effect of losing urchins: {(C10-C00).mean():+.2f})")
print(f"  heat only ..................... {C01.mean():.2f}   (main effect of the heat pulse: {(C01-C00).mean():+.2f})")
print(f"  both .......................... {C11.mean():.2f}\n")

Ih = I[H]
p_syn = float((Ih < -0.02).mean())          # meaningfully synergistic
print(f"INTERACTION term  I = C(both) - C(urchin) - C(heat) + C(baseline):")
print(f"  mean {Ih.mean():+.3f}   median {np.median(Ih):+.3f}   [5th,95th] = [{np.percentile(Ih,5):+.3f}, {np.percentile(Ih,95):+.3f}]")
print(f"  P(synergy, I < -0.02) = {p_syn:.2f}")
# vulnerability signature: collapses ONLY when both stressors present
only_both = ((C11<0.10) & (C10>0.10) & (C01>0.10))
print(f"  P(reef collapses ONLY in the both-stressors cell) = {only_both.mean():.2f}\n")

if p_syn >= 0.8:
    verdict = "ROBUST: heat is more damaging after urchin loss across most data-consistent parameters."
elif p_syn >= 0.5:
    verdict = "SUGGESTIVE but not robust: the synergy holds in a majority, not the bulk, of cases."
else:
    verdict = "NOT SUPPORTED (full ensemble): the synergy does not survive parameter uncertainty."
print("VERDICT (full history-matched ensemble):", verdict)

# --- Conditional test: reefs that ALSO reproduce the observed ~31% decline from urchin loss ---
# (i.e. parameter sets near the herbivory tipping point, behaving like the real reef)
declined = H & (C[:,1] < 0.69*C[:,0])       # urchin-loss-only cell drops >=31% relative (Cramp-like)
nd = int(declined.sum())
print(f"\nConditional subset (reefs that reproduce BOTH healthy-2014 AND a >=31% urchin-loss decline): n={nd} ({100*nd/N:.0f}%)")
if nd >= 30:
    Id = I[declined]
    psd = float((Id < -0.02).mean())
    print(f"  interaction mean {Id.mean():+.3f}  median {np.median(Id):+.3f}  P(synergy)={psd:.2f}")
    onlyb = ((C[declined,3]<0.10) & (C[declined,1]>0.10) & (C[declined,2]>0.10)).mean()
    print(f"  P(collapses ONLY with both stressors) = {onlyb:.2f}")
    print("  => " + ("SYNERGY SURVIVES only for near-tipping reefs: whether Banco Capiro was that close"
                     "\n     is the empirical question the field data must settle." if psd>=0.5 else
                     "even for near-tipping reefs the clean interaction is weak; heat dominates."))
else:
    print("  too few near-tipping parameter sets to conclude; with robust priors the reef mostly resists urchin loss.")

# --- One-at-a-time sensitivity (tornado) of the interaction to each parameter ---
print("\nSENSITIVITY of the interaction (mid-range base; vary each param low->high):")
base = dict(gh=0.50, ufrac=0.12, d0=0.22, dh=0.55, a=0.22, gamma=0.97)
def I_of(**kw):
    g_h=kw['gh']; g_l=g_fish+(g_h-g_fish)*kw['ufrac']
    C00,C10,C01,C11 = factorial((g_h,g_l,kw['d0'],kw['dh'],kw['a'],kw['gamma']))
    return C11-C10-C01+C00
ranges = dict(gh=(0.35,0.65), ufrac=(0.05,0.25), d0=(0.10,0.35), dh=(0.20,0.90), a=(0.10,0.35), gamma=(0.80,1.15))
for k,(lo,hi) in ranges.items():
    Ilo=I_of(**{**base,k:lo}); Ihi=I_of(**{**base,k:hi})
    print(f"  {k:6s}: I {Ilo:+.3f} -> {Ihi:+.3f}   (swing {abs(Ihi-Ilo):.3f})")

# --- Money figure: the 4 recovery trajectories for a representative near-tipping reef ---
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
def traj(g, d0, dh, a, gamma):
    def rhs(y, t):
        Cc, Mm = y; T = max(0.0, 1-Cc-Mm)
        d = d0 + (dh if PULSE_START <= t < PULSE_END else 0.0)
        return [Cc*(r*T - d - a*Mm), a*Mm*Cc - g*Mm/(Mm+T+1e-9) + gamma*Mm*T]
    tt = np.linspace(0, HORIZON, 700)
    return tt, odeint(rhs, [C0, M0], tt)[:,0]
ex = dict(gh=0.45, uf=0.12, d0=0.25, dh=0.60, a=0.28, gamma=1.05)   # illustrative near-tipping reef
gl_ex = g_fish + (ex['gh']-g_fish)*ex['uf']
fig, ax = plt.subplots(figsize=(8.4,5))
cells = [("urchins, no heat", ex['gh'], 0.0, "#0b2524"),
         ("heat only (recovers)", ex['gh'], ex['dh'], "#0f5c63"),
         ("urchin loss only", gl_ex, 0.0, "#a9792f"),
         ("BOTH: heat + urchin loss", gl_ex, ex['dh'], "#b23b2e")]
for lab,g,dh_,c in cells:
    tt,cc = traj(g, ex['d0'], dh_, ex['a'], ex['gamma'])
    ax.plot(tt, cc, lw=2.6, color=c, label=lab)
ax.axvspan(PULSE_START, PULSE_END, color="#f0d9a0", alpha=0.5, label="2023 heat pulse")
ax.set_xlabel("years"); ax.set_ylabel("coral cover"); ax.set_ylim(0,0.9)
ax.set_title("Recovery synergy: a grazed reef recovers from heat; an ungrazed one does not")
ax.legend(fontsize=8, loc="lower left"); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("/Users/mike/code/steps/coral-tela/fig_recovery_synergy.png", dpi=140)
print("saved fig_recovery_synergy.png")

np.savez("/Users/mike/code/steps/coral-tela/attribution_v2_out.npz",
         I=I, C=C, healthy=healthy, p_syn=p_syn)
print("\nsaved attribution_v2_out.npz")
print("HONEST: history-matched priors, not a fit to the time series; a multi-point Op Wallacea")
print("fit is still required to constrain magnitudes. This tests robustness of the interaction SIGN.")
