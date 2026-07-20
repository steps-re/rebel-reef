# Sediment-diversion model — VM job spec (Banco Capiro / Tela Bay)

## Scientific question
Leading published hypothesis for Banco Capiro's survival: local currents **divert the
Ulúa River sediment plume around** the reef so it isn't smothered/shaded to death,
even though the bay as a whole is turbid. Test whether virtual sediment released at
the Ulúa/Chamelecón mouth actually reaches the Banco Capiro bank, and with what
residence time / concentration, vs being swept past by the along-shore Caribbean Current.

## Geography (decimal degrees)
- **Release (Ulúa–Chamelecón mouth):** 15.92 N, -87.68 W (continuous line source, jitter ±0.03°)
- **Banco Capiro target box:** lat 15.83–15.97, lon -87.53 to -87.40
- **Cocalito target box (W bay, closest to river):** lat 15.90–15.98, lon -87.58 to -87.50
- **Fetch domain:** lat 15.4–16.3, lon -88.1 to -86.9
- Prevailing flow: Caribbean Current runs **E→W (westward)** along the Honduran coast;
  the Ulúa mouth sits **west** of Tela Bay, so a naive westward current would carry the
  plume *away* from Tela — the hypothesis is that eddies/coastal setup do something else.

## Data
GLORYS12 reanalysis via copernicusmarine (creds in `~/marine-cdr/sim/.cmenv`):
`cmems_mod_glo_phy_my_0.083deg_P1D-m`, vars **uo, vo** (surface, shallowest depth),
**daily 2019-01-01 → 2023-12-31** (covers the 2023 heatwave), the fetch domain box.
Small box → small download.

## Method — REUSE the proven harness, don't rewrite parcels from scratch
Adapt `~/marine-cdr/sim/residence_sim.py` (or tracer_sim3.py) which already handles
FieldSet.from_xarray_dataset + JITParticle + a DeleteOOB kernel. Known gotchas from
that work: JITParticle needed (Scipy too slow) but **JIT segfaults on monthly fields
and on grid-release with custom fields**; use DAILY fields (stable) and a modest point
release. AdvectionRK4, continuous release (repeatdt ~ daily), track each cohort ~60 days.

## Outputs (save to gs://airloom-marine-cdr/coral-tela/ AND print)
1. **Fraction of released particles that enter the Banco Capiro box** within 60 days
   (and separately the Cocalito box). Low fraction = "plume diverted" hypothesis supported.
2. **Mean residence time** of any particles that do enter the bank box.
3. A **plume-density heatmap** (particle-days per cell) over the domain → fig_plume.png.
4. Seasonal split (wet season May–Nov vs dry) since river discharge peaks in the wet season.

## Hard caveat to report honestly
GLORYS is 1/12° (~8 km); Tela Bay is ~20 km wide → only ~2–3 cells resolve it. This
model shows **regional along-shore transport direction**, NOT fine sub-bay circulation.
State this limit plainly (same class of limitation as the CDR shelf-sea runs). The
fine-scale "sand kicked up locally" shading is covered by the separate turbidity model.

## Housekeeping
Run under nohup, sync results to GCS, then **STOP the VM** (`gcloud compute instances
stop marine-cdr-vm`) when done. Account = mike@airloom.energy, project ai-engineering-team-491520.
