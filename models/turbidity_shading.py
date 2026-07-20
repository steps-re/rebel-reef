"""
First-principles model #4a: turbidity as photoprotection ("turbid-water refugium").

Coral bleaching is a LIGHT x TEMPERATURE synergy: under heat stress, excess PAR
drives reactive-oxygen production in the symbionts -> bleaching. Lowering light
raises the temperature/DHW threshold at which bleaching happens (Cacciapaglia &
van Woesik 2016; Sully & van Woesik 2020). Tela Bay is chronically turbid from
the Ulua plume + resuspended sand. Hypothesis: that turbidity shades the corals
enough to blunt the photo-oxidative stress that their measured DHW (peaked ~14 in
2023) would otherwise cause.

Physics: Beer-Lambert light attenuation PAR(z) = PAR0 * exp(-Kd * z).
We compare Tela (turbid, high Kd) to a clear-water neighbor (Utila/Roatan) at the
same coral depths, form a light fraction L = PAR_tela(z)/PAR_clear(z), and define a
light-weighted effective thermal dose DHW_eff = DHW_measured * L. Then see whether
turbidity pulls Tela's effective dose from the mortality band (>8) down toward the
survivable band.
"""
import numpy as np

# Diffuse attenuation coefficients Kd (1/m) for PAR
# UPDATED to MODIS-Aqua measured values (ocean_color.py, 2003-2022):
#   Kd490 clear reefs ~0.049 -> Kd_PAR ~0.09 ; Banco Capiro Kd490 ~0.122 -> Kd_PAR ~0.14
#   event/flood p90 Kd490 ~0.22 -> Kd_PAR ~0.22 (episodic resuspension/plume)
Kd_clear  = 0.09    # measured clear-reef baseline (Utila/Roatan/Cayos)
Kd_tela   = 0.14    # measured Banco Capiro monthly mean
Kd_tela_hi= 0.22    # measured Tela flood/resuspension p90 (episodic strong shading)

depths = np.array([3, 5, 8, 10, 12, 15, 20, 30])   # m; Banco Capiro spans ~5-30 m

def light_fraction(Kd_turb, Kd_ref, z):
    """PAR at depth z under turbid water relative to clear water at same depth."""
    return np.exp(-(Kd_turb - Kd_ref) * z)

print("="*74)
print("TURBIDITY SHADING — light fraction reaching coral vs a clear-water reef")
print("="*74)
print(f"{'depth m':>8}{'L (Kd=0.30)':>14}{'L (Kd=0.45)':>14}   (fraction of clear-reef light)")
for z in depths:
    L1 = light_fraction(Kd_tela, Kd_clear, z)
    L2 = light_fraction(Kd_tela_hi, Kd_clear, z)
    print(f"{z:>8}{L1:>14.2f}{L2:>14.2f}")

# --- Light-weighted effective thermal dose ---
# Measured 2023 peak DHW at Banco Capiro (from CRW daily 5km) ~ 14 C-weeks.
DHW_measured = 14.0
print(f"\nMeasured 2023 peak DHW at Banco Capiro = {DHW_measured:.0f} C-weeks "
      f"(bleaching>4, severe/mortality>8)")
print("Light-weighted EFFECTIVE dose DHW_eff = DHW * L  (approximates the photo-")
print("oxidative stress corals actually experience under shade):\n")
print(f"{'depth m':>8}{'DHW_eff Kd=0.30':>18}{'DHW_eff Kd=0.45':>18}{'band':>14}")
for z in depths:
    e1 = DHW_measured * light_fraction(Kd_tela, Kd_clear, z)
    e2 = DHW_measured * light_fraction(Kd_tela_hi, Kd_clear, z)
    band = ("mortality" if e1 > 8 else "bleaching" if e1 > 4 else "sub-bleaching")
    print(f"{z:>8}{e1:>18.1f}{e2:>18.1f}{band:>14}")

# --- Depth at which turbidity brings effective dose below the bleaching line ---
zz = np.linspace(1, 30, 300)
for Kd, tag in [(Kd_tela, "0.30"), (Kd_tela_hi, "0.45")]:
    eff = DHW_measured * light_fraction(Kd, Kd_clear, zz)
    z4 = zz[eff < 4]
    z8 = zz[eff < 8]
    d4 = z4.min() if z4.size else np.inf
    d8 = z8.min() if z8.size else np.inf
    print(f"\nKd={tag}: effective dose < 8 (mortality) below {d8:.1f} m; "
          f"< 4 (bleaching) below {d4:.1f} m")

print("""
READ-OUT:
- A clear-water reef at DHW 14 is squarely in the mortality band at all depths.
- Tela's turbidity cuts the light so that below ~8-12 m the light-weighted dose
  drops into the bleaching/sub-bleaching band -> the deeper bank corals are
  effectively shaded from the heatwave they measurably experienced.
- This is the mechanism that reconciles "DHW 14 yet no mass bleaching": the stress
  is thermal AND radiative, and Tela removes the radiative half.
- TRIP MEASUREMENT this generates: Secchi depth / Kd (PAR logger) at Banco Capiro
  vs a clear reference reef, and note bleaching-vs-depth. If shallow (<8 m) corals
  bleach more than deep ones during heat, that is the fingerprint of this mechanism.
""")
