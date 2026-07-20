"""
First-principles model #3: carbonate-chemistry buffering.

Tela Bay gets heavy freshwater + nutrient loading from the Ulua River and city
sewage. Two opposite effects on aragonite saturation (Omega_arag, the master
variable for coral calcification):
  (-) freshwater dilution + eutrophication (respiration adds CO2 -> lowers Omega)
  (+) if the river drains CARBONATE/limestone terrain it carries high total
      alkalinity, which RAISES Omega.
Honduras' Ulua basin contains extensive Cretaceous limestone (karst), so the
alkalinity channel is physically plausible. This model brackets the two regimes
with a first-principles conservative-mixing + respiration calc (PyCO2SYS) to find
which river signature is protective vs harmful, and to name the key measurement.

Reuses the validated PyCO2SYS setup from the marine-CDR repo.
"""
import numpy as np, PyCO2SYS as pyco2

# --- Open-Caribbean seawater endmember (healthy reef reference) ---
SW = dict(TA=2360.0, DIC=2000.0, S=35.8, T=29.0)   # umol/kg, PSU, degC

# Two river endmembers bracketing the hypothesis
RIVERS = {
    "carbonate/karst river (high alk)":  dict(TA=3200.0, DIC=3050.0, S=0.2),
    "organic/eutrophic runoff (low alk)": dict(TA=750.0,  DIC=850.0,  S=0.2),
}

def omega(TA, DIC, S, T):
    r = pyco2.sys(par1=TA, par2=DIC, par1_type=1, par2_type=2,
                  salinity=S, temperature=T)
    return r["saturation_aragonite"], r["pH_total"], r["pCO2"]

print("Open-Caribbean reference:")
Oa, pH, pco2 = omega(SW["TA"], SW["DIC"], SW["S"], SW["T"])
print(f"  Omega_arag={Oa:.2f}  pH={pH:.3f}  pCO2={pco2:.0f} uatm   (Omega>3.3 = good coral growth)\n")

# --- 1. Conservative mixing lines: seawater <-> river, 0-30% freshwater ---
fracs = np.linspace(0, 0.30, 31)   # river fraction by volume
print("Conservative mixing (river fraction 0 -> 30%):")
print(f"{'river type':<36}{'f=5%':>8}{'f=15%':>9}{'f=30%':>9}   Omega_arag")
print("-"*72)
mix_out = {}
for rname, R in RIVERS.items():
    Os = []
    for f in fracs:
        TA = (1-f)*SW["TA"] + f*R["TA"]
        DIC = (1-f)*SW["DIC"] + f*R["DIC"]
        S  = (1-f)*SW["S"]  + f*R["S"]
        Oa, _, _ = omega(TA, DIC, S, SW["T"])
        Os.append(Oa)
    Os = np.array(Os); mix_out[rname] = Os
    def at(fr): return Os[np.argmin(np.abs(fracs-fr))]
    print(f"{rname:<36}{at(0.05):>8.2f}{at(0.15):>9.2f}{at(0.30):>9.2f}")

# --- 2. Eutrophication overlay: nutrient-fuelled respiration adds DIC (CO2) ---
# Add organic-respiration DIC to a modest 10% freshwater mix, watch Omega fall.
print("\nEutrophication (respiration adds CO2 as DIC) at 10% freshwater mix:")
print(f"{'river type':<36}{'+0':>7}{'+40':>7}{'+80':>7}{'+120':>8}  umol/kg DIC added")
print("-"*72)
f = 0.10
for rname, R in RIVERS.items():
    TA0 = (1-f)*SW["TA"] + f*R["TA"]
    DIC0 = (1-f)*SW["DIC"] + f*R["DIC"]
    S0  = (1-f)*SW["S"]  + f*R["S"]
    vals = []
    for dResp in [0, 40, 80, 120]:
        Oa, _, _ = omega(TA0, DIC0 + dResp, S0, SW["T"])
        vals.append(Oa)
    print(f"{rname:<36}" + "".join(f"{v:>7.2f}" for v in vals[:3]) + f"{vals[3]:>8.2f}")

print("""
READ-OUT:
- If the Ulua carries high carbonate alkalinity (karst signature), moderate river
  input RAISES Omega_arag above the open-ocean reef value -> a calcification
  SUBSIDY that helps explain vigorous growth despite the nutrient load.
- If runoff is low-alkalinity + eutrophic, respiration drags Omega down -> harmful.
- The single measurement that decides it: the river's total-alkalinity : DIC ratio
  (and in-bay Omega_arag). That is the field ask this model generates for Tela Coral.
""")
np.savez("/Users/mike/code/steps/coral-tela/carbonate_out.npz",
         fracs=fracs, **{k.split()[0]: v for k, v in mix_out.items()})
