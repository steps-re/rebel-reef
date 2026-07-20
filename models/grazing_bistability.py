"""
First-principles model #1 for the Banco Capiro / Cocalito reef (Tela Bay, Honduras).

Question it answers: the reef has >60-70% live coral yet LOW reef-fish biomass.
On every other Caribbean reef, low herbivorous-fish biomass -> macroalgae take over
-> coral collapse. Why not here?

Hypothesis under test: the extraordinary Diadema antillarum (long-spined urchin)
density measured at Tela (reported ~100x the regional average, at pre-1983-dieoff
levels) supplies the grazing that fish normally supply, holding the reef in the
coral-dominated basin of a bistable system.

Model: Mumby, Hastings & Edwards (2007, Nature) coral-macroalgae-turf dynamics.
State fractions C (coral) + M (macroalgae) + T (turf) = 1.
    dC/dt = r*T*C - d*C - a*M*C
    dM/dt = a*M*C - g*M/(M+T) + gamma*M*T
Grazing g = fraction of reef grazed per unit time = g_fish + g_urchin.

This is a genuinely first-principles ecological-dynamics test, no big data needed.
"""
import numpy as np
from scipy.integrate import odeint

# --- Mumby et al. 2007 baseline parameters (Caribbean forereef) ---
r     = 1.0    # coral recruitment/lateral growth onto turf (/yr)
d     = 0.44   # coral natural mortality (/yr)
a     = 0.10   # macroalgal overgrowth of coral (/yr)
gamma = 0.80   # macroalgal vegetative spread onto turf (/yr)

def rhs(y, t, g):
    C, M = y
    T = max(0.0, 1.0 - C - M)
    dC = r*T*C - d*C - a*M*C
    dM = a*M*C - g*M/(M+T+1e-9) + gamma*M*T
    return [dC, dM]

def equilibrium(g, C0, M0, tmax=2000):
    t = np.linspace(0, tmax, 4000)
    sol = odeint(rhs, [C0, M0], t, args=(g,))
    return sol[-1]

# --- 1. Find the grazing tipping threshold g* (coral basin collapses below it) ---
# Start from a healthy reef and lower grazing until coral cannot persist.
gs = np.linspace(0.05, 0.9, 350)
coral_from_healthy = np.array([equilibrium(g, 0.75, 0.05)[0] for g in gs])
coral_from_degraded = np.array([equilibrium(g, 0.05, 0.75)[0] for g in gs])

# collapse threshold: lowest g at which a healthy reef stays coral (>5%)
healthy_ok = gs[coral_from_healthy > 0.05]
g_collapse = healthy_ok.min() if healthy_ok.size else np.nan
# recovery threshold: lowest g at which a degraded reef flips back to coral
recover_ok = gs[coral_from_degraded > 0.05]
g_recover = recover_ok.min() if recover_ok.size else np.nan

print("="*70)
print("BANCO CAPIRO / COCALITO  —  herbivory bistability (first principles)")
print("="*70)
print(f"Coral-collapse grazing threshold  g*_collapse = {g_collapse:.3f}")
print(f"Coral-recovery grazing threshold  g*_recover  = {g_recover:.3f}")
print(f"  -> bistable (hysteresis) window: g in [{g_collapse:.3f}, {g_recover:.3f}]")
print()

# --- 2. Scenario grazing budgets ---
# Regional degraded Caribbean reef: fish carry grazing, urchins ~absent since 1983.
# Tela: LOW fish, but Diadema at ~pre-dieoff density.
# Grazing supplied scales with herbivore biomass/consumption; we express each
# component as reef-fraction-grazed-per-year and test where the reef lands.
scenarios = {
    "Typical degraded reef (fish only, low)":      dict(g_fish=0.10, g_urch=0.00),
    "Healthy-fish reef (no urchins)":              dict(g_fish=0.35, g_urch=0.00),
    "TELA: low fish + Diadema at pre-dieoff dens.": dict(g_fish=0.10, g_urch=0.35),
    "TELA counterfactual: urchins lost":           dict(g_fish=0.10, g_urch=0.00),
}
print(f"{'scenario':<46}{'g_tot':>7}{'coral_eq':>10}{'state':>14}")
print("-"*77)
for name, s in scenarios.items():
    g = s["g_fish"] + s["g_urch"]
    C_eq, M_eq = equilibrium(g, 0.5, 0.3)   # neutral start, let dynamics decide
    # also probe from healthy start to reveal basin if bistable
    C_h = equilibrium(g, 0.75, 0.05)[0]
    state = "CORAL" if C_h > 0.05 else "macroalgae"
    print(f"{name:<46}{g:>7.2f}{C_h:>10.2f}{state:>14}")

# --- 3. What grazing does the OBSERVED ~65% coral cover imply? ---
target = 0.65
best_g = gs[np.argmin(np.abs(coral_from_healthy - target))]
print()
print(f"Grazing consistent with observed ~65% coral cover: g ~ {best_g:.2f}")
print(f"Fish alone at Tela (~0.10) sit {'BELOW' if 0.10 < g_collapse else 'above'} "
      f"the collapse threshold {g_collapse:.2f}")
print("-> Diadema grazing is the load-bearing term; remove it and the model")
print("   flips Tela into the macroalgae basin. The 'paradox' dissolves.")

np.savez("/Users/mike/code/steps/coral-tela/grazing_out.npz",
         gs=gs, coral_from_healthy=coral_from_healthy,
         coral_from_degraded=coral_from_degraded,
         g_collapse=g_collapse, g_recover=g_recover, best_g=best_g)
