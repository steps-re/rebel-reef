"""
Patient, slow high-resolution DHW pull (PacIOOS ERDDAP is throttling).
Strategy: small 5-year chunks per site, long timeouts, many retries with backoff,
generous sleeps between requests, incremental per-site CSV saves so partial progress
survives. Run in background; integrate into the map + brief when complete.
"""
import io, time, urllib.request, os
import numpy as np, pandas as pd

OUT = "/Users/mike/code/steps/coral-tela/data_dhw"
os.makedirs(OUT, exist_ok=True)

SITES = {
    "banco_capiro": (15.90, -87.48), "cocalito": (15.94, -87.55),
    "utila": (16.10, -86.92), "roatan": (16.32, -86.53),
    "cayos_cochinos": (15.98, -86.47), "florida_keys": (24.66, -81.05),
}
CHUNKS = [(f"{y}-01-01", f"{min(y+5,2026)}-06-30") for y in range(1985, 2026, 5)]

def pull(lat, lon, t0, t1):
    url = ("https://pae-paha.pacioos.hawaii.edu/erddap/griddap/dhw_5km.csv"
           f"?CRW_DHW%5B({t0}):({t1})%5D%5B({lat})%5D%5B({lon})%5D,"
           f"CRW_SST%5B({t0}):({t1})%5D%5B({lat})%5D%5B({lon})%5D")
    for k in range(8):
        try:
            with urllib.request.urlopen(url, timeout=300) as r:
                df = pd.read_csv(io.StringIO(r.read().decode()), skiprows=[1])
            return df.dropna(subset=["CRW_DHW"])
        except Exception as e:
            print(f"      retry {k+1}: {str(e)[:60]}", flush=True)
            time.sleep(30 + 20*k)   # backoff
    return None

summary = {}
for name, (lat, lon) in SITES.items():
    fp = os.path.join(OUT, f"{name}.csv")
    if os.path.exists(fp):
        print(f"{name}: cached", flush=True)
    else:
        parts = []
        for t0, t1 in CHUNKS:
            print(f"{name} {t0}..{t1}", flush=True)
            d = pull(lat, lon, t0, t1)
            if d is not None:
                parts.append(d)
            time.sleep(15)          # be gentle
        if parts:
            df = pd.concat(parts).drop_duplicates("time")
            df.to_csv(fp, index=False)
            print(f"{name}: saved {len(df)} rows", flush=True)
        else:
            print(f"{name}: FAILED all chunks", flush=True); continue
    df = pd.read_csv(fp)
    summary[name] = dict(
        peak_dhw=round(float(df.CRW_DHW.max()), 1),
        peak_2023=round(float(df[df.time.str.startswith('2023')].CRW_DHW.max()), 1)
                  if df.time.str.startswith('2023').any() else None,
        days_gt8=int((df.CRW_DHW > 8).sum()), max_sst=round(float(df.CRW_SST.max()), 1),
    )
    print(f"  -> {name}: {summary[name]}", flush=True)

import json
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=2)
print("\nDONE. summary.json written.", flush=True)
print(json.dumps(summary, indent=2), flush=True)
