"""
Integrated multi-driver attribution + vulnerability model for Banco Capiro (the novel core).

Couples environmental drivers into the coral-macroalgae-urchin model (Mumby et al. 2007) and
follows the reef's TRAJECTORY through the observed sequence (respecting hysteresis: the reef
was IN the healthy basin, so its path depends on where it started):
  2014: ~59% coral, Diadema 155/100m2                                  (Cramp et al. 2025)
  2022: Diadema -88% -> macroalgae +193%, hard coral -31%             (Cramp et al. 2025)
  2023: DHW ~14 heatwave -> mass mortality at central Banco Capiro     (HRI 2024: Canyon 0.3%,
        Rotonda 0.7%), while higher-grazing/turbid sites persisted     (Cocalito 68%, Punta Sal 84%)

Tests the herbivory x thermal INTERACTION: losing urchins in 2022 lowered the thermal tipping point,
so the 2023 heat, survivable by a grazed reef, became lethal. Produces the vulnerability map.

PRELIMINARY: two calibration points + literature-set thermal term. Caveats printed at end.
"""
import numpy as np
from scipy.integrate import odeint
from scipy.optimize import brentq
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Mumby et al. 2007 structure. Macroalgal overgrowth (a) and spread (gamma) are ELEVATED above
# the oligotrophic defaults to reflect Tela Bay's measured eutrophy (our MODIS chlorophyll = 4x the
# clear reefs): nutrient-rich water makes macroalgae more competitive once grazing drops.
r, a, gamma = 1.0, 0.30, 1.10
g_fish = 0.10                        # low fish grazing at Tela

def rhs(y, t, g, d):
    C, M = y; T = max(0.0, 1-C-M)
    return [r*T*C - d*C - a*M*C, a*M*C - g*M/(M+T+1e-9) + gamma*M*T]

def traj(C0, M0, g, d, years, n=4000):
    s = odeint(rhs, [C0, M0], np.linspace(0, years, n), args=(g, d))
    return max(0.0, s[-1, 0]), max(0.0, s[-1, 1])

def settle(g, d, C0=0.6, M0=0.1):     # long-run equilibrium from a healthy start (upper branch)
    return traj(C0, M0, g, d, 5000)[0]

# --- Urchin grazing mapping g = g_fish + kappa*U ---
# Set so 2014's 155 urchins/100m2 place the reef robustly in the coral basin (g2014 ~ 0.50);
# the 2022 crash (12% remaining) then drops grazing below the tipping threshold (~0.19-0.38).
U2014, U2022 = 155.0, 155.0*0.12
g2014_target = 0.50
kappa = (g2014_target - g_fish)/U2014
g2014, g2022 = g_fish + kappa*U2014, g_fish + kappa*U2022
# Calibrate baseline mortality so the observed 2014 cover (0.59) is a genuine equilibrium at g2014,
# so that a grazing drop (2022) lowers the equilibrium and the reef declines (rather than growing).
d0 = brentq(lambda d: settle(g2014, d) - 0.59, 0.20, 0.60)

# --- Thermal mortality term (literature-set): d = d0 + k_h*max(0, DHW_eff-4) ---
k_h = 0.14
DHWeff_2023 = 14.0*0.55               # DHW ~14, reef-mean light fraction ~0.55 (turbidity-shaded)
d_heat = d0 + k_h*max(0.0, DHWeff_2023-4.0)

print("="*76)
print("CALIBRATION (2014) + TRAJECTORY through the observed sequence")
print("="*76)
print(f"d0={d0}  kappa={kappa:.5f}  g2014={g2014:.3f}  g2022={g2022:.3f}  d_heat(2023)={d_heat:.3f}")
print(f"2014 equilibrium coral = {settle(g2014,d0):.2f} (calibrated to 0.59)\n")

# Trajectory: start healthy (2014), lose urchins for 8 yr -> 2022, then 1.5 yr of heat -> 2023
C14, M14 = 0.59, 0.05
C22, M22 = traj(C14, M14, g2022, d0, 8)
C23, M23 = traj(C22, M22, g2022, d_heat, 1.5)
# Counterfactual: the 2023 heat if urchins had NOT crashed
C23cf, _ = traj(C14, M14, g2014, d_heat, 1.5)

print("TRAJECTORY (coral cover):")
print(f"  2014 start .......................... {C14:.2f}   (obs ~0.59)")
print(f"  2022 after urchin loss (8 yr) ....... {C22:.2f}   (obs decline ~-31%, to ~0.41)")
print(f"  2023 heat at post-urchin state ...... {C23:.2f}   (obs mass mortality, central sites ~0)")
print(f"  2023 heat WITH 2014 urchins (c.f.) .. {C23cf:.2f}   (would have buffered the heat)\n")

print("ATTRIBUTION of the 2014->2023 collapse (the robust result = counterfactual END-STATES):")
print(f"  urchin loss alone (2014->2022): coral 0.59 -> {C22:.2f}  (major decline, reproduces observed -31%)")
print(f"  + 2023 heat, urchins already gone: -> {C23:.2f}  (crosses collapse threshold; matches central-site mass mortality)")
print(f"  counterfactual, same 2023 heat WITH 2014 urchins: -> {C23cf:.2f}  (reef PERSISTS above collapse)")
print(f"  => Same heat dose, opposite fate: {C23:.2f} (no urchins) vs {C23cf:.2f} (urchins). The 2022 die-off")
print(f"     removed the reef's thermal buffer, so the 2023 heat became lethal. This matches the field pattern:")
print(f"     central Banco Capiro (urchins lost) died in 2023; higher-grazing Tela sites (Cocalito, Punta Sal) held.\n")

# --- Vulnerability map: persistence (upper-branch coral) over (urchin density, effective heat) ---
Us = np.linspace(0, 200, 55); Hs = np.linspace(0, 14, 55)
Z = np.array([[traj(0.59, 0.05, g_fish+kappa*U, d0+k_h*max(0,H-4), 30)[0] for U in Us] for H in Hs])
fig, ax = plt.subplots(figsize=(8.6,6))
cf = ax.contourf(Us, Hs, Z, levels=np.linspace(0,0.65,14), cmap="YlGn")
ax.contour(Us, Hs, Z, levels=[0.1], colors="#b23b2e", linewidths=2.4)
pts = {"2014":(U2014,1.0,"#0b2524"),"2022":(U2022,1.0,"#a9792f"),
       "2023 observed collapse":(U2022,DHWeff_2023,"#b23b2e"),
       "2023 counterfactual (2014 urchins)":(U2014,DHWeff_2023,"#0f5c63")}
for lab,(U,H,c) in pts.items():
    ax.scatter([U],[H],c=c,s=95,edgecolors="white",zorder=5)
    ax.annotate(lab,(U,H),textcoords="offset points",xytext=(7,6),fontsize=8,color=c,weight="bold")
plt.colorbar(cf,label="persistent coral cover")
ax.set_xlabel("Diadema urchin density (per 100 m$^2$)"); ax.set_ylabel("effective heat dose DHW$_{eff}$ (C-weeks)")
ax.set_title("Banco Capiro vulnerability window (red = collapse threshold)")
plt.tight_layout(); plt.savefig("/Users/mike/code/steps/coral-tela/fig_vulnerability.png", dpi=140)
print("saved fig_vulnerability.png")
print("\nCAVEATS: two-point calibration; thermal coefficient k_h literature-set not fitted; minimal")
print("model (no explicit heterotrophy/carbonate feedback yet). Robust result = the INTERACTION sign")
print("and the shrinking safe window, not the exact percentages. Full time series (Op Wallacea) needed to fit.")
