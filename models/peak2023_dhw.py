import io, urllib.request, pandas as pd
SITES={"Banco Capiro":(15.90,-87.48),"Cocalito":(15.94,-87.55),"Utila":(16.10,-86.92),
"Roatan":(16.32,-86.53),"Cayos Cochinos":(15.98,-86.47),"Florida Keys":(24.66,-81.05)}
B=("https://pae-paha.pacioos.hawaii.edu/erddap/griddap/dhw_5km.csv?"
   "CRW_DHW%5B(2023-01-01):(2024-02-28)%5D%5B({la})%5D%5B({lo})%5D,"
   "CRW_SST%5B(2023-01-01):(2024-02-28)%5D%5B({la})%5D%5B({lo})%5D")
out={}
for n,(la,lo) in SITES.items():
    for k in range(4):
        try:
            with urllib.request.urlopen(B.format(la=la,lo=lo),timeout=90) as r:
                df=pd.read_csv(io.StringIO(r.read().decode()),skiprows=[1])
            df=df.dropna(subset=["CRW_DHW"])
            out[n]=dict(peakDHW=round(float(df.CRW_DHW.max()),1),
                        maxSST=round(float(df.CRW_SST.max()),1),
                        days_gt8=int((df.CRW_DHW>8).sum()))
            print(f"  {n:<16} peakDHW2023={out[n]['peakDHW']:5.1f}  maxSST={out[n]['maxSST']:.1f}  days>8={out[n]['days_gt8']}")
            break
        except Exception as e:
            print(f"   retry {k+1} {n}: {str(e)[:50]}")
import json; json.dump(out,open("peak2023_dhw.json","w"),indent=2)
print("saved peak2023_dhw.json")
