# Adversarial review — Banco Capiro integrated attribution model

**Reviewer role:** skeptical senior coral-reef ecologist / quantitative modeler, acting as a hostile peer reviewer for *Coral Reefs*.
**Verdict up front:** The headline result ("same heat, opposite fate") is **not a finding of the model — it is a construction of the setup.** The two-point calibration constrains almost nothing, several key parameters are asserted rather than fitted, and the live site (`science.html`) states the natural-experiment result as a *validation* when it is at best a plausibility sketch. In its current form this is **not publishable** in *Coral Reefs* as an attribution study. It could become a modest, honest "conceptual model + hypothesis" note if the overclaims are stripped and a real sensitivity/identifiability analysis is added.

Findings are ranked most-severe first. File/line citations are to the versions read on 2026-07-20.

---

## 1. [FATAL] The "same heat, opposite fate" result is an artifact of the counterfactual construction, not of the herbivory×heat interaction

**Where:** `integrated_attribution.py` lines 62–79.

```python
C14, M14 = 0.59, 0.05
C22, M22 = traj(C14, M14, g2022, d0, 8)      # 8 yr of collapsed grazing
C23, M23 = traj(C22, M22, g2022, d_heat, 1.5)   # heat applied to the ALREADY-DECLINED state
C23cf, _ = traj(C14, M14, g2014, d_heat, 1.5)   # heat applied to the FULL-COVER 2014 state
```

The observed arm (`C23`) applies the heat to a reef that has **already spent 8 model-years losing coral to macroalgae** (it enters 2023 at `C22`, which the code itself expects to be ~0.41). The counterfactual arm (`C23cf`) applies the *same* heat term but **starts over from the pristine 0.59/0.05 state with full grazing and only 1.5 years of clock**. So the two endpoints differ for at least three reasons that have nothing to do with a thermal *tipping-point* interaction:

- different **starting coral cover** (C22 vs 0.59),
- different **starting macroalgae** (M22, grown for 8 yr, vs 0.05),
- different **grazing** during the 1.5-yr heat window (g2022 vs g2014).

The claim on line 79–81 — *"Same heat dose, opposite fate ... The 2022 die-off removed the reef's thermal buffer, so the 2023 heat became lethal"* — attributes the entire gap to the thermal buffer. But the model has **confounded the heat effect with 8 years of prior grazing-driven decline and macroalgal accumulation.** You cannot separate "the heat was survivable with urchins" from "the reef simply had more coral and less algae to begin with in the counterfactual."

**Why it's wrong:** A genuine interaction test holds everything else fixed and toggles one factor. The correct counterfactual is: take the **same 2023 starting state** (`C22, M22`) and apply the heat under `g2014` vs `g2022` — OR apply the heat to the pristine state under both grazing levels. As written, the comparison is between two *different reefs at two different points on their trajectories*, so "opposite fate" is nearly guaranteed by arithmetic.

**What would fix it:** Report a proper factorial: (start state) × (grazing during heat) × (heat on/off), with everything else held constant, and show the marginal effect of grazing *at a common baseline*. If the "buffer" effect survives when you hold C0/M0 fixed, you have a result. Right now you do not know that it does.

---

## 2. [FATAL] `d0` is calibrated to a starting condition that already equals the target — the calibration does no work

**Where:** lines 37–38 and 49.

```python
def settle(g, d, C0=0.6, M0=0.1):    # starts at C=0.60
    return traj(C0, M0, g, d, 5000)[0]
d0 = brentq(lambda d: settle(g2014, d) - 0.59, 0.20, 0.60)
```

You solve for the mortality `d0` that makes the long-run equilibrium equal 0.59, **starting the integration from C=0.60** — i.e., one percentage point away from the answer, inside the coral basin by construction. Because Mumby-type dynamics are bistable and you seeded the upper basin, `settle` will land on the upper branch for a wide range of `d`, and `brentq` simply picks the `d` that pins the upper-branch equilibrium to 0.59. This is not a calibration against data; it is **choosing a parameter so that an assumed number is reproduced.** The "2014 equilibrium coral = 0.59 (calibrated to 0.59)" print on line 60 is a tautology, not a validation.

**Why it's wrong:** With one equation (equilibrium = 0.59) and one free parameter (`d0`), the fit is exact and uninformative. It tells you nothing about whether the model structure is right, and it guarantees a "match" that a reader may mistake for corroboration.

**What would fix it:** `d0` must be constrained by something *independent* of the 0.59 target — e.g., an in-situ coral mortality estimate, or a joint fit to multiple observables (coral AND macroalgae AND urchin trajectory across ≥3 time points). A single-point pin is not a fit.

---

## 3. [FATAL] Two data points cannot identify five-plus free parameters — the model is unidentifiable

**Where:** parameters `r, a, gamma, g_fish, kappa, d0, k_h` (lines 26–54).

The manuscript (OUTLINE.md core-claim 3, and line 15 of the model docstring) calls this a "natural-experiment calibration and validation." The actual data content is: 2014 coral ≈0.59, urchins 155; 2022 urchins ≈19 (12%), coral "−31%"; 2023 "mass mortality" at central sites. That is effectively **two-to-three scalar observations.** The model has at least seven adjustable quantities:

- `a=0.30`, `gamma=1.10` — set by hand "to reflect eutrophy" (line 26), **not fitted**;
- `g_fish=0.10` — asserted (line 27);
- `g2014_target=0.50` → sets `kappa` (lines 45–46) — **assumed**, not measured;
- `d0` — pinned to 0.59 (see Finding 2);
- `k_h=0.14` — "literature-set" (line 52), **no citation, not fitted**;
- the `0.55` light fraction in `DHWeff_2023` (line 53) — asserted.

Everything that matters (the tipping threshold's location, the width of the "safe window") is a function of `a`, `gamma`, `kappa`, and `k_h`, **none of which the two data points constrain.** `a` and `gamma` are confounded with `kappa` (algal aggressiveness vs. grazing both move the tipping point); `k_h` and the `0.55` light fraction are perfectly confounded (only their product `k_h·0.55·(14−4)` enters). The claim of "calibration" is not supported by the information content of the data.

**What would fix it:** State plainly that the model is **not identified** from the available data, or obtain the full Op Wallacea 2018–2024 annual time series (coral, macroalgae, urchin, fish per year) and *jointly* fit with priors and reported parameter uncertainty. Until then, drop the words "calibration" and "validation."

---

## 4. [SEVERE] The "eutrophy" parameters `a` and `gamma` were raised specifically to make macroalgae win — this is tuning-to-fit dressed as mechanism

**Where:** lines 24–26 vs. `grazing_bistability.py` lines 26–28.

The base model uses `a=0.10, gamma=0.80` (Mumby forereef defaults, `grazing_bistability.py`). The integrated model **raises them to `a=0.30, gamma=1.10`** with the justification "to reflect Tela Bay's measured eutrophy ... MODIS chlorophyll = 4× the clear reefs." But:

- 4× chlorophyll → 3× overgrowth rate and +38% spread is an **unjustified quantitative leap.** There is no calibration mapping chlorophyll to `a` or `gamma`; the numbers are chosen, and they are exactly the numbers that make the 2022 grazing crash flip the reef to algae. This is the definition of tuning-to-fit.
- Tripling `a` moves the tipping threshold and is precisely what makes "lose urchins → collapse" happen on the model's timescale. So the headline mechanism rides on hand-set parameters.
- The lit review (`lit_review.md` §5, §2) is explicit that **there is no measured N/P or turbidity dataset for Tela**, and that the chlorophyll/nutrient story rests on grey literature and media. So even the "4× eutrophy" premise feeding these parameters is not on firm quantitative ground for driving a rate constant.

**What would fix it:** A sensitivity sweep over `a ∈ [0.10, 0.30]`, `gamma ∈ [0.80, 1.10]` showing whether the qualitative result (collapse on urchin loss; "opposite fate") survives at the *literature-default* values. If it only appears at the elevated values, the result is an assumption, not a finding, and must be reported as such.

---

## 5. [SEVERE] `k_h` and the effective-DHW light fraction are asserted, uncited, and mutually confounded — yet they set whether 2023 is "lethal"

**Where:** lines 51–54.

```python
k_h = 0.14                          # "literature-set" — no reference given anywhere
DHWeff_2023 = 14.0*0.55             # 0.55 "reef-mean light fraction" — asserted
d_heat = d0 + k_h*max(0.0, DHWeff_2023-4.0)
```

- `k_h=0.14` is labeled "literature-set (not fitted)" (docstring line 15; comment line 51) but **no source is cited in the code, the lit review, or science.html.** A reviewer cannot check it. The thermal-mortality slope is the single number that decides whether `d_heat` crosses the collapse threshold, i.e., whether the reef "dies" in 2023.
- The `0.55` light fraction is a **single reef-mean value** invented here; the actual `turbidity_shading.py` shows the shading fraction ranges from ~0.4 (deep, high Kd) to ~0.9+ (shallow) — there is no single 0.55, and it is applied uniformly to a reef the model elsewhere says is depth-structured (5–30 m).
- `k_h` and `0.55` enter **only as a product**. They are non-identifiable individually. Presenting them as two independent "physical" inputs is misleading.

**What would fix it:** Cite the source for `k_h` (and show the DHW→mortality dose-response it comes from, with its uncertainty), or fit it. Replace the scalar `0.55` with the depth distribution the shading model already produces, and propagate. Report the result's sensitivity to the combined product.

---

## 6. [SEVERE] The site presents the natural experiment as "validation" of the model; it is not

**Where:** `science.html` lines 50–54.

> "**The counterfactual then happened for real.** ... The reef slipped exactly as the model predicts when grazing drops below threshold, **a natural-experiment validation of the herbivory mechanism** ..."

This is an overclaim. The model was **built after** the 2022 outcome was known, and its parameters (`a`, `gamma`, `kappa`, `d0`) were chosen so that losing urchins produces decline. A model tuned to reproduce an outcome and then described as "validated" by that same outcome is **circular.** Validation requires prediction of *out-of-sample* data the model was not tuned on. The 2014→2022 decline is the calibration target, not an independent test.

Additional specific overclaim in the same passage: "the reef slipped **exactly** as the model predicts." The model's own printout targets a −31% decline because that is the observed number it was aimed at; "exactly" is reproducing the input.

**What would fix it:** Reword to "consistent with" and label it calibration, not validation. A true validation would hold out, e.g., the 2023 or 2024 Op Wallacea benthic values and show the model predicts them without being fit to them.

---

## 7. [SEVERE] Alternative explanations for the 2022–2023 decline are neither modeled nor ruled out

The model attributes the collapse to **urchin loss → lowered thermal tipping point.** The following competing explanations are ignored, and the model cannot distinguish them from its favored story:

- **Direct 2023 heat, urchin-independent.** DHW ~14 is in the mass-mortality band on its own (the site's own §2 says so). Mass bleaching mortality of adult coral in 2023 needs **no** herbivory-mediated tipping point — heat kills coral directly. The model *assumes* the heat was "survivable with urchins" purely because it set `k_h` and the light fraction low enough that `C23cf` stays up. That is assumed, not shown.
- **SCTLD / other coral disease.** The lit review (`lit_review.md` §A1 caveats) explicitly warns that Cramp et al. do **not** attribute a cause and that SCTLD-susceptible species declined at Utila. Stony Coral Tissue Loss Disease could drive central-Banco-Capiro coral loss independent of urchins or macroalgae. Not in the model.
- **Storm/physical damage** in 2022–2023. Not considered.
- **Macroalgae-independent overgrowth timing.** The model needs 8 years of algal takeover to reach C22≈0.41, but the observed decline is 2014→2022 with the *urchin* crash only in 2022 (Caribbean-wide die-off, `lit_review.md` §B). The model runs `g2022` for the **full 8 years** (line 64), i.e., it assumes urchins were functionally gone the whole time, which contradicts the die-off timing (urchins crashed in 2022, not 2014). This is a **structural mismatch between the model's forcing timeline and the documented event chronology.**

**What would fix it:** Add heat-only and disease-only counterfactuals and show the herbivory pathway explains variance the alternatives cannot. Fix the forcing chronology so grazing collapses in 2022, not 2014.

---

## 8. [SEVERE] Site-comparability confound: "central Banco Capiro died, western Tela held" is treated as evidence for the model, but the sites differ in ways the model ignores

**Where:** `science.html` lines 79–81 of `integrated_attribution.py` narrative; `datasets.md` §2 table.

The clinching field pattern is: Canyon 0.3%, Rotonda 0.7% (dead) vs Cocalito 68%, Punta Sal 84% (held). The model's story is "central sites lost urchins → lost thermal buffer → died." But `datasets.md` shows these are **different reefs 10–13 km apart** (central Banco Capiro at 15.86°N vs western Tela at 15.91°N), with different depth, exposure, and — critically — the western sites have **near-zero macroalgae (Punta Sal 1.2%, Prolifera 0.8%)** and much higher coral. There is no evidence in hand that the western sites *had the same urchin trajectory*, the same DHW, or the same turbidity. Attributing the central/western contrast to the urchin-buffer mechanism is an **ecological-fallacy / site-selection confound**: you are comparing non-comparable sites and crediting your mechanism.

Furthermore (`lit_review.md` §A1, `datasets.md` §2): the 2022 Cramp "−31%" is a **percent change of unknown base** (could be →28% or →41%); the 2014 "59%" and the 2023 HRI per-site values come from **different survey programs** (Cramp/Opwall vs HRI/AGRRA) which may not be methodologically or spatially comparable. The model treats them as one clean time series for one place.

**What would fix it:** Restrict the comparison to sites with matched monitoring, matched DHW, and measured urchin trajectories, or explicitly acknowledge the comparison is between non-equivalent sites and cannot isolate the mechanism.

---

## 9. [MAJOR] `science.html` §6 states hydrodynamic/upwelling results as findings, but no such model output is in the reviewed code

**Where:** `science.html` lines 119–135, 141–142, 160–162, and the "What we've ruled out" table.

The site asserts precise numbers: "~53% of particles reach the reef," "flush through in ~4 days," "no cool subsurface pool ... downwelling-favorable." **None of the six model files provided produce these outputs** (no GLORYS/Parcels code was among the files to review). Either the code exists elsewhere and was not shown, or these are placeholder numbers presented as results. For a manuscript targeting *Coral Reefs*, the "~53%" and "~4 days" must trace to reproducible code with stated GLORYS12 configuration. The site's own caveat (1/12° ≈ 8 km, "bay is only ~2–3 cells") actually **undercuts** the precision of "~53%/~4 days" — at 2–3 cells you cannot credibly resolve a 53% split or a 4-day residence for a ~20 km bay.

**What would fix it:** Provide the plume/upwelling code and either widen the reported precision to match 8-km resolution or downgrade the claims to qualitative.

---

## 10. [MAJOR] Thermal "same SST" claim leans on monthly climatology and a non-standard DHW analog

**Where:** `thermal_stress.py` lines 61–66; `science.html` lines 67–70.

The site claims Banco Capiro's MMM (29.65 °C) is "statistically indistinguishable" from degrading reefs (29.45–29.54 °C) — but the code computes **no statistical test**; it prints point values and calls a 0.1–0.2 °C difference "indistinguishable" by eye. The DHW figure quoted publicly is "DHW ≈ 14," but `thermal_stress.py` computes a **non-standard "DHW analog"** (3-month trailing sum of monthly anomalies, line 64), which is **not** the NOAA CRW 12-week DHW. Meanwhile `turbidity_shading.py` and `integrated_attribution.py` hardcode `DHW_measured = 14.0` from "CRW daily 5km" — a different product than `thermal_stress.py` actually pulls (monthly). So the "14" driving the whole attribution is **asserted, not produced by the shown thermal code.**

Also note the site (§2) claims the reef "did not bleach out" at DHW 14 in 2023, while the model and Opwall/HRI data say **central Banco Capiro suffered mass mortality in 2023**. The public "it felt the same heat and lived anyway" framing is contradicted by the study's own premise that the central sites died. This is an internal inconsistency between the "thriving" marketing framing and the "high but declining/collapsed" data.

**What would fix it:** Compute an actual daily CRW DHW time series and an actual statistical comparison; reconcile the "lived anyway" claim with the documented 2023 mortality.

---

## 11. [MAJOR] Results are stated as assumptions echoed back (the "is it a result or an input?" test)

Concrete instances where an assumption is presented as a result:

- **"2014 equilibrium coral = 0.59 (calibrated to 0.59)"** (line 60) — input echoed.
- **"reproduces observed −31%"** (line 76) — `a`, `gamma`, `d0` were set to hit this; it is the target, not a prediction.
- **"g ≈ 0.19 collapse threshold"** on the site (§1) comes from `grazing_bistability.py` with the *default* `a/gamma`, but the integrated model uses elevated `a/gamma`, which **moves** that threshold. The site quotes the threshold from one parameterization and the collapse story from another.
- **"turbidity removes the radiative half" / DHW_eff below bleaching band** (`turbidity_shading.py`) — this is a direct consequence of the assumed `Kd_tela=0.14` and the assumption that stress scales linearly with light fraction; no coral-response data validates the linear `DHW_eff = DHW·L` form.

---

## 12. [MODERATE] Minor modeling / numerical issues

- **Macroalgae grazing term** `g*M/(M+T+1e-9)` (line 31): when both M and T → 0 the term is well-behaved via the epsilon, but the `1e-9` guard silently changes dynamics near the boundary; better to handle the empty-substrate case explicitly.
- **`M14 = 0.05` vs `M22` grown over 8 yr**: the initial macroalgae for the counterfactual (0.05) and the trajectory start are the same, but the observed arm carries `M22` — reinforcing Finding 1's confound.
- **No stochasticity / no confidence intervals anywhere.** Every number is a point estimate from a deterministic ODE with hand-set parameters. For an attribution claim this is unacceptable; attribution requires uncertainty.
- **`settle(..., 5000)` and `traj(..., 5000, n=4000)`**: 5000 "years" integrated with 4000 steps (~1.25 yr/step) is coarse for a system with r=1/yr; check that the equilibrium is numerically converged and not step-size dependent.
- **Vulnerability map (lines 84–85)** inherits every unidentified parameter (`kappa`, `d0`, `k_h`, elevated `a/gamma`); the "shrinking safe window" is therefore a picture of the assumptions, not a measured window.

---

## 13. Things that are actually fine (briefly)

- The **honest caveats** printed at the end of the model (lines 100–102) and in the lit review are genuinely good and unusually candid: two-point calibration, `k_h` not fitted, minimal model, "full time series needed." The problem is that the **site and outline do not carry these caveats forward** with the same honesty — the site says "validation," the caveats say "preliminary."
- The **lit review** (`lit_review.md`) is careful, flags UNVERIFIED items, and correctly refuses to attribute the urchin die-off cause to Cramp et al. This is good practice and should govern the manuscript.
- The **Mumby et al. 2007 base model** in `grazing_bistability.py` uses defensible published defaults and is a reasonable qualitative backbone.
- The **turbidity/optics and carbonate scripts** are honestly framed as brackets and "field asks," not results — that framing is appropriate. The problem is only when their assumed outputs (`0.55`, `Kd=0.14`) are hard-wired into the attribution as if measured.
- The **outline's positioning note** ("do not overclaim novelty on mechanisms") shows awareness; it just isn't applied to the novelty of *attribution*, which is where the overclaim actually lives.

---

## What a reviewer would demand before this is publishable

1. **A real identifiability statement.** Show, formally, which parameters the available data constrain (answer: essentially none of the ones that matter). Stop calling two points a "calibration/validation."
2. **Full Op Wallacea 2018–2024 annual time series** (coral, macroalgae, urchin, fish) and a **joint fit** across ≥4 time points with reported parameter posteriors/uncertainty. Co-authorship route is already noted in the outline — this is a hard gate, not optional.
3. **Global sensitivity analysis** (e.g., Sobol/Morris) over `a, gamma, g_fish, kappa, k_h, light-fraction, d0`, reporting whether the "opposite fate" and "shrinking window" survive at literature-default parameters. If they only appear at the tuned values, say so and reframe as hypothesis.
4. **A corrected, factorial counterfactual** (Finding 1): common baseline state, toggle grazing and heat independently, report marginal effects with CIs.
5. **A source and uncertainty for `k_h`**, and replacement of the scalar `0.55` light fraction with the depth-resolved distribution, propagated.
6. **Competing-hypothesis tests** (Finding 7): heat-only, disease/SCTLD, storm — shown to explain less variance than the herbivory pathway, or acknowledged as indistinguishable.
7. **Site-comparability analysis** (Finding 8): matched DHW, matched urchin data, matched monitoring protocol before any central-vs-western inference.
8. **The hydrodynamic code** (Finding 9) with stated GLORYS12 config and precision honestly bounded to 8-km resolution.
9. **Reconcile the public "thriving / lived anyway" framing** with the study's own finding that central Banco Capiro suffered mass mortality in 2023. Right now the marketing and the science contradict each other.
10. **Independent validation**: hold out at least one year of benthic data the model was not fit to and predict it.

**Bottom line:** The interaction *hypothesis* (losing the keystone grazer lowers the reef's effective thermal tipping point) is scientifically interesting and worth pursuing. But as implemented, the model **assumes its conclusion** through the counterfactual construction (Finding 1), a tautological calibration (Finding 2), and hand-set parameters chosen to produce the target (Findings 4, 5). The "same heat, opposite fate" result and the site's "natural-experiment validation" language are not supported. Reframe as a preliminary conceptual model and hypothesis, add the identifiability/sensitivity work, fit a real time series, or do not submit as an "attribution."
