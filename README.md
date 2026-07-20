# Rebel Reef — why Banco Capiro survives

First-principles models of why the **Banco Capiro / Cocalito** reef in **Tela Bay, Honduras**
holds 60–70% live coral in warm, turbid, sewage-fed water that is degrading the clear-water
reefs 30–60 km away.

**Live site:** https://steps-re.github.io/rebel-reef/
**For:** the [Tela Coral](https://steps-re.github.io/rebel-reef/) expedition & documentary (Tiffany Duong).

## The finding in one paragraph

Banco Capiro is *not* a thermal refuge — 40 years of satellite SST show it is as warm as its
degrading neighbors, and it hit **Degree Heating Weeks ≈ 14** (mass-mortality level) in the 2023
heatwave and lived. Two "physical escape" hypotheses also fail: currents do **not** divert the Ulúa
river plume (it reaches the reef but flushes through in ~4 days), and there is **no** cool upwelling.
What remains is **local biology and optics**: turbidity that shades the coral, nutrients the coral can
eat (heterotrophy), an extraordinary *Diadema* urchin population that grazes back seaweed, and likely a
heat-tolerant symbiont (the one mechanism requiring genetics to confirm).

## Repository layout

| Path | Contents |
|---|---|
| `index.html`, `*.html`, `style.css` | The public site (Overview, Science, Glossary, Media, Researchers) |
| `models/` | Each model as a runnable Python script + the VM-model method spec |
| `data/` | Processed outputs: per-site metrics (CSV/JSON) and figures |

## Models

| Script | What it does |
|---|---|
| `models/grazing_bistability.py` | Coral–macroalgae–urchin bistability (Mumby et al. 2007); shows urchins hold the coral state |
| `models/thermal_stress.py` | 40-yr CoralTemp SST → MMM, DHW, thermal variability vs neighbor reefs |
| `models/daily_dhw.py`, `patient_dhw.py`, `peak2023_dhw.py` | Daily DHW pulls (the real heat-stress dose) |
| `models/ocean_color.py` | MODIS-Aqua turbidity (Kd490) + chlorophyll comparison |
| `models/turbidity_shading.py` | Light × heat bleaching model using measured clarity |
| `models/carbonate.py` | PyCO2SYS carbonate-chemistry mixing (river alkalinity vs eutrophication) |
| `models/tela_sediment_SPEC.md` | Method spec for the Lagrangian sediment-plume + upwelling model (run on GLORYS12 + Parcels) |

The Lagrangian sediment/upwelling model outputs are in `data/` (`plume_*`, `upwell_*`, figures);
the run scripts are available on request.

## Reproduce

Self-contained models (herbivory, thermal, ocean-color, turbidity, carbonate) need only:

```
python3.11 -m venv .venv && . .venv/bin/activate
pip install numpy scipy pandas matplotlib PyCO2SYS
python models/grazing_bistability.py     # etc.
```

The Lagrangian model additionally needs `copernicusmarine parcels xarray netCDF4` and a free
Copernicus Marine account. Data pullers hit public NOAA/NASA ERDDAP endpoints (no auth).
Note: script paths are currently absolute to the author's machine; adjust as needed.

## Data sources (all open)

- **NOAA Coral Reef Watch 5 km** — SST & Degree Heating Weeks (NOAA / PacIOOS ERDDAP)
- **NASA MODIS-Aqua** — Kd490 turbidity & chlorophyll (NOAA CoastWatch ERDDAP)
- **Copernicus GLORYS12** — currents, subsurface temperature, upwelling
- **Coral Reef Alliance / Operation Wallacea** — coral cover & *Diadema* density (field surveys)

## Honest caveats (v1, pre-expedition)

- This is a modeling draft, **not peer-reviewed**. Site-specific claims await field validation.
- GLORYS is 1/12° (~8 km); Tela Bay resolves in ~2–3 cells → regional transport only, not sub-bay flow.
- The turbidity Kd was first assumed, then **corrected** to the MODIS-measured value (weaker shading than the
  first pass) — an example of the adversarial checking the project applies.
- Neighbor daily-DHW series is still being pulled (ERDDAP throttling); Banco Capiro's 2023 DHW is measured.

## License

Code: **MIT** (see `LICENSE`). Processed data, figures and text: **CC-BY 4.0**.

## Credits

Reef & expedition: **Tela Coral** (Tiffany Duong). Modeling & site: **Steps Ventures**.
Built with Claude Code.
