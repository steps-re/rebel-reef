"""
Satellite ocean-color analysis: is Tela Bay measurably different at the surface?

Two MODIS-Aqua products (4km monthly, 2003-2022) via CoastWatch ERDDAP:
  - k490  = diffuse light attenuation at 490nm = TURBIDITY / water clarity
            (grounds the turbidity-shading model, which assumed Kd~0.30)
  - chlorophyll = phytoplankton = NUTRIENT / eutrophication proxy (pollution signal)

Compare Banco Capiro/Cocalito to the clear-water reefs that are degrading nearby.
If Tela is BOTH more turbid AND more chlorophyll-rich, that quantifies "the polluted,
murky bay" — and (paradoxically) the turbidity is exactly what shades the corals.
"""
import io, time, urllib.request
import numpy as np, pandas as pd

DS = {
    "k490":        ("erdMH1kd490mday", "k490"),
    "chlorophyll": ("erdMH1chlamday",  "chlorophyll"),
}
T0, T1 = "2003-01-16", "2022-01-16"

SITES = {
    "Banco Capiro (Tela)": (15.90, -87.48),
    "Cocalito (Tela W)":   (15.94, -87.55),
    "Utila (Bay Is.)":     (16.10, -86.92),
    "Roatan (Bay Is.)":    (16.32, -86.53),
    "Cayos Cochinos":      (15.98, -86.47),
    "Florida Keys":        (24.66, -81.05),
}

def fetch(dsid, var, lat, lon, tries=4):
    url = (f"https://coastwatch.pfeg.noaa.gov/erddap/griddap/{dsid}.csv"
           f"?{var}%5B({T0}):({T1})%5D%5B({lat})%5D%5B({lon})%5D")
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                df = pd.read_csv(io.StringIO(r.read().decode()), skiprows=[1])
            df["time"] = pd.to_datetime(df["time"])
            return df.dropna(subset=[var])
        except Exception as e:
            print(f"    retry {k+1} {var} {lat},{lon}: {str(e)[:70]}"); time.sleep(3)
    return None

# Kd490 -> Kd_PAR (approx, for coastal water): Kd_PAR ~ 0.75 * Kd490 + 0.05
def kd_par(kd490): return 0.75*kd490 + 0.05

rows = {}
for name, (lat, lon) in SITES.items():
    rec = {}
    for key, (dsid, var) in DS.items():
        df = fetch(dsid, var, lat, lon)
        if df is None or len(df) < 12:
            rec[key] = np.nan; continue
        vals = df[var].values
        rec[key+"_mean"] = float(np.nanmean(vals))
        rec[key+"_p90"]  = float(np.nanpercentile(vals, 90))
    rows[name] = rec
    kd = rec.get("k490_mean", np.nan)
    print(f"  {name:<22} Kd490={kd:.3f} (~Kd_PAR {kd_par(kd):.2f})  "
          f"chl={rec.get('chlorophyll_mean', np.nan):.2f} mg/m3")

print("\n" + "="*82)
print("SURFACE OPTICS — turbidity (Kd490) and productivity (chlorophyll), 2003-2022")
print("="*82)
tab = pd.DataFrame(rows).T
tab["Kd_PAR_approx"] = kd_par(tab["k490_mean"])
show = tab[["k490_mean","k490_p90","Kd_PAR_approx","chlorophyll_mean","chlorophyll_p90"]].round(3)
print(show.to_string())
tab.to_csv("/Users/mike/code/steps/coral-tela/ocean_color_metrics.csv")

# Relative to the clear-reef mean (Utila/Roatan/Cayos)
clear = ["Utila (Bay Is.)","Roatan (Bay Is.)","Cayos Cochinos"]
kd_clear = np.nanmean([rows[c].get("k490_mean",np.nan) for c in clear])
chl_clear= np.nanmean([rows[c].get("chlorophyll_mean",np.nan) for c in clear])
print(f"\nClear-reef baseline: Kd490={kd_clear:.3f}, chl={chl_clear:.2f}")
for site in ["Banco Capiro (Tela)","Cocalito (Tela W)"]:
    kx = rows[site].get("k490_mean",np.nan); cx = rows[site].get("chlorophyll_mean",np.nan)
    print(f"  {site:<22} turbidity {kx/kd_clear:.1f}x  chlorophyll {cx/chl_clear:.1f}x clear reefs")
print("""
-> If Tela is several-x more turbid + chlorophyll-rich than the healthy clear reefs,
   the satellite CONFIRMS a distinct 'murky, nutrient-loaded' surface signature -
   and that turbidity is the shade in the light x heat model. Real Kd replaces the
   assumed 0.30, so we can re-run the shading depths with measured values.
""")
