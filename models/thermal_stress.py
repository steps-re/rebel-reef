"""
First-principles model #2: the thermal paradox.

Banco Capiro/Cocalito hits ~31C summer SST — hot enough to bleach reefs elsewhere —
yet bleaches rarely. Test the leading physical hypothesis: it is a THERMALLY
VARIABLE site, and corals on high-variance reefs are pre-hardened to heat
(the "variability refugia" idea; Oliver & Palumbi 2011, Safaie et al. 2018).

Data: NOAA Coral Reef Watch 5km monthly SST v3.1, 1985-2026, via CoastWatch ERDDAP
(no auth). We pull a point time series for Banco Capiro and comparison reefs that
DID bleach / degrade, then compute for each:
  - MMM  (max of the 12 monthly climatological means)   = bleaching reference
  - a monthly DHW analog: 3-month trailing sum of positive (SST - MMM), in C-months
  - thermal variability: SD of the monthly climatology + mean seasonal range
  - warm-season SST reached
Reuses the ERSST/OISST time-series + climatology approach from the eel/turtle work.
"""
import io, time, urllib.request
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = ("https://coastwatch.pfeg.noaa.gov/erddap/griddap/NOAA_DHW_monthly.csv"
        "?sea_surface_temperature%5B(1985-01-16):(2026-06-16)%5D"
        "%5B({lat})%5D%5B({lon})%5D")

SITES = {
    # name: (lat, lon, note)
    "Banco Capiro (Tela)":  (15.90, -87.48, "the mystery reef, >60% cover"),
    "Cocalito (Tela W)":    (15.94, -87.55, "elkhorn 'Rebel Reef'"),
    "Utila (Bay Is.)":      (16.10, -86.92, "~20% cover, degraded"),
    "Roatan (Bay Is.)":     (16.32, -86.53, "sponge disease 2018"),
    "Cayos Cochinos":       (15.98, -86.47, "MPA reference"),
    "Florida Keys":         (24.66, -81.05, "SCTLD + 2023 bleaching"),
}

def fetch(lat, lon, tries=4):
    url = BASE.format(lat=lat, lon=lon)
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                raw = r.read().decode()
            df = pd.read_csv(io.StringIO(raw), skiprows=[1])  # row1 = units
            df = df.rename(columns={"sea_surface_temperature": "sst"})
            df["time"] = pd.to_datetime(df["time"])
            df = df.dropna(subset=["sst"])
            return df[["time", "sst"]]
        except Exception as e:
            print(f"   retry {k+1} {lat},{lon}: {e}")
            time.sleep(3)
    return None

def metrics(df):
    df = df.copy()
    df["month"] = df["time"].dt.month
    clim = df.groupby("month")["sst"].mean()           # monthly climatology
    mmm = clim.max()                                    # max monthly mean
    seas_range = clim.max() - clim.min()               # seasonal amplitude
    clim_sd = clim.std()                               # among-month variability
    df["hotspot"] = (df["sst"] - mmm).clip(lower=0)
    # monthly DHW analog: trailing 3-month sum of positive anomalies (C-months)
    df = df.sort_values("time")
    df["dhw_analog"] = df["hotspot"].rolling(3, min_periods=1).sum()
    peak_dhw = df["dhw_analog"].max()
    max_sst = df["sst"].max()
    n_bleach_months = int((df["sst"] > mmm + 1.0).sum())  # months >1C over MMM
    return dict(mmm=mmm, seas_range=seas_range, clim_sd=clim_sd,
                peak_dhw=peak_dhw, max_sst=max_sst,
                n_bleach_months=n_bleach_months, df=df)

rows = {}
print("Pulling CoralTemp 5km monthly SST (1985-2026)...")
for name, (lat, lon, note) in SITES.items():
    df = fetch(lat, lon)
    if df is None or len(df) < 100:
        print(f"  {name:<22} FAILED / masked"); continue
    m = metrics(df)
    rows[name] = m
    print(f"  {name:<22} n={len(df):3d}  MMM={m['mmm']:.2f}  maxSST={m['max_sst']:.2f}"
          f"  seasRange={m['seas_range']:.2f}  climSD={m['clim_sd']:.2f}"
          f"  peakDHWanalog={m['peak_dhw']:.1f}  months>MMM+1={m['n_bleach_months']}")

# --- Summary table ---
print("\n" + "="*88)
print("THERMAL-STRESS COMPARISON  (higher seasRange/climSD = more variability-hardened)")
print("="*88)
tab = pd.DataFrame({k: {c: v[c] for c in
        ["mmm","max_sst","seas_range","clim_sd","peak_dhw","n_bleach_months"]}
        for k, v in rows.items()}).T
tab = tab.round(2)
print(tab.to_string())
tab.to_csv("/Users/mike/code/steps/coral-tela/thermal_metrics.csv")

# --- Figure: seasonal climatology (variability) per site ---
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
months = np.arange(1, 13)
for name, m in rows.items():
    clim = m["df"].groupby("month")["sst"].mean().reindex(months)
    hot = "Banco" in name or "Cocalito" in name
    ax[0].plot(months, clim.values, marker="o", lw=2.5 if hot else 1.2,
               label=name, alpha=0.95 if hot else 0.6)
ax[0].set_title("Monthly SST climatology (1985-2026)")
ax[0].set_xlabel("month"); ax[0].set_ylabel("SST (C)"); ax[0].legend(fontsize=7)
ax[0].grid(alpha=0.3)

names = list(rows.keys())
sr = [rows[n]["seas_range"] for n in names]
cols = ["#c0392b" if ("Banco" in n or "Cocalito" in n) else "#7f8c8d" for n in names]
ax[1].barh(names, sr, color=cols)
ax[1].set_title("Seasonal thermal range (variability-hardening proxy)")
ax[1].set_xlabel("max-min monthly SST (C)")
ax[1].invert_yaxis(); ax[1].grid(alpha=0.3, axis="x")
plt.tight_layout()
plt.savefig("/Users/mike/code/steps/coral-tela/thermal_fig.png", dpi=130)
print("\nsaved thermal_metrics.csv + thermal_fig.png")
