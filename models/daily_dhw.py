"""
The real thermal-stress test: daily 5km Coral Reef Watch DHW, 1985-2026.
Monthly SST smoothed away the heatwave peaks; the daily DHW product is the
operational bleaching-stress metric (DHW>4 = bleaching expected, >8 = severe +
mortality). Pull daily CRW_DHW + CRW_SST for Banco Capiro vs the reefs that
bleached/degraded around it, and ask: did Banco Capiro get LESS thermal dose
(thermal refugium) or the SAME dose and survive anyway (local biology/light)?

Source: PacIOOS ERDDAP dhw_5km (NOAA CRW v3.1), no auth.
"""
import io, time, urllib.request
import numpy as np, pandas as pd

BASE = ("https://pae-paha.pacioos.hawaii.edu/erddap/griddap/dhw_5km.csv"
        "?CRW_DHW%5B(1985-04-01):({end})%5D%5B({lat})%5D%5B({lon})%5D,"
        "CRW_SST%5B(1985-04-01):({end})%5D%5B({lat})%5D%5B({lon})%5D")
END = "2026-06-30"

SITES = {
    "Banco Capiro (Tela)": (15.90, -87.48),
    "Cocalito (Tela W)":   (15.94, -87.55),
    "Utila (Bay Is.)":     (16.10, -86.92),
    "Roatan (Bay Is.)":    (16.32, -86.53),
    "Cayos Cochinos":      (15.98, -86.47),
    "Florida Keys":        (24.66, -81.05),
}

def fetch(lat, lon, tries=4):
    url = BASE.format(lat=lat, lon=lon, end=END)
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                df = pd.read_csv(io.StringIO(r.read().decode()), skiprows=[1])
            df["time"] = pd.to_datetime(df["time"])
            return df.dropna(subset=["CRW_DHW"])
        except Exception as e:
            print(f"   retry {k+1}: {e}"); time.sleep(4)
    return None

recs = {}
for name, (lat, lon) in SITES.items():
    df = fetch(lat, lon)
    if df is None or len(df) < 1000:
        print(f"  {name:<22} FAILED"); continue
    df["year"] = df["time"].dt.year
    peak = df["CRW_DHW"].max()
    peak_when = df.loc[df["CRW_DHW"].idxmax(), "time"].date()
    peak2023 = df.loc[df["year"] == 2023, "CRW_DHW"].max()
    d_gt4 = int((df["CRW_DHW"] > 4).sum())
    d_gt8 = int((df["CRW_DHW"] > 8).sum())
    maxsst = df["CRW_SST"].max()
    recs[name] = dict(peak=peak, peak_when=str(peak_when), peak2023=peak2023,
                      days_gt4=d_gt4, days_gt8=d_gt8, maxsst=maxsst, n=len(df))
    print(f"  {name:<22} n={len(df):5d} peakDHW={peak:5.1f} ({peak_when}) "
          f"2023={peak2023:5.1f} d>4={d_gt4:4d} d>8={d_gt8:4d} maxSST={maxsst:.1f}")

print("\n" + "="*94)
print("DAILY DHW — real bleaching-stress dose. If Banco Capiro's dose ~= degraded"
      "\nneighbors, the thermal environment is NOT the protector (local mechanism).")
print("="*94)
tab = pd.DataFrame(recs).T[["peak","peak2023","days_gt4","days_gt8","maxsst"]]
print(tab.to_string())
tab.to_csv("/Users/mike/code/steps/coral-tela/daily_dhw_metrics.csv")
