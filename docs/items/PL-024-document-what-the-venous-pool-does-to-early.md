---
id: PL-024
title: Document what the venous pool does to early mixed-venous readings
priority: P2
effort: S
status: done
classes: docs, ux
feature: chart-readout
touches: docs/MODEL.md, docs/references/README.md, tests/unit/test_blood.py
added: 2026-08-24
closed: 2026-11-22
pr: 2266
tests: tests/unit/test_blood.py::test_the_venous_pool_lag_in_the_first_minutes_is_small_beside_tissue_uptake
not-delegable: two judgments no command can make: whether the first-minute lag is framed as a modelling artifact or as the lumped stand-in for venous transit, checked against Davis and Mapleson 1981, and whether the Mixed venous readout gains a cue; a grep could pin only a sentence chosen before either is settled
---

> **Groomed 2026-09-22 (`PL-Y4YG`): still owed, but the numbers below are for
> a pool that no longer exists.** The venous pool is 1.222 L, not 1.0 L: Davis
> and Mapleson's combined venous pool (*Br J Anaesth* 1981;53:399–405) was
> adopted on 2026-09-07 (`PL-8ZJQ`), and `docs/MODEL.md` records that at the
> stored 5.0 L/min "the mixed-venous time constant moves from 12.0 s to 14.7
> s". The 55/34/17% figures were measured against 1.0 L and must be
> re-measured before any of them reaches `docs/MODEL.md`, and **Why it
> matters**'s "1.0 L is the Gas Man reference value" is superseded by the same
> adoption. Neither § "Venous blood" nor § "Known limitations" yet says what
> the pool does to the first minute, so the item stands.
>
> One framing point for whoever writes the note: with the pool now a published
> physiologic volume rather than a program default, the early lag is arguably
> the model's lumped stand-in for venous transit rather than an artifact, so
> check the framing against Davis and Mapleson before calling it either. What
> a learner needs either way is that a low mixed-venous reading in the first
> minute is mostly the pool's residence time, not tissue uptake. The readout
> is `ReadoutPanel("Mixed venous", ...)` in `app/dashboard_frame.py`, whose
> qualifier slot is empty, and the trace is `app/chart_frame.py`'s; `touches`
> names the first in place of `app/simulation_view.py`.

**Problem.** The venous pool's mixing time constant — 60 · V/Q̇ = 12 s at the
reference 1.0 L and 5 L/min — dominates the displayed mixed-venous value
through the first minute of wash-in. Against a near-instant-mixing
comparison it reads 55% low at 30 s, 34% low at 60 s, and 17% low at 120 s.
Mixed venous is displayed both as a metric and as a chart trace, and neither
`docs/MODEL.md` § "Known limitations" nor the interface says the early curve
is a mixing artifact rather than tissue uptake.
**Why it matters.** Not a defect: 1.0 L is the Gas Man reference value and
is cited twice in `reference_adult.json`. But a learner reading the first
minute of that trace as uptake draws a wrong conclusion from a correct
number, which is the presentation half of the safety standard rather than a
numerical error. Reported as `P2-4`.
**Where.** `docs/MODEL.md` ("Known limitations", "Venous blood"),
`app/simulation_view.py` (the mixed-venous metric and trace).
**First step.** Write the `docs/MODEL.md` note — it is the smaller half and
needs no interface decision. Whether the display also needs a cue is the
open question, and it can be answered after.
**Done when.** `docs/MODEL.md` states the pool's time constant and its
effect on the first minute, and any interface cue is a deliberate decision
rather than an omission.

**Checked 2026-11-22** against `d4e8200`: still applies, but its figures are out of date. Neither `docs/MODEL.md` § "Known limitations" nor `docs/INTERFACE.md` says that the first minute of the mixed-venous trace is shaped by the venous pool's mixing. The stored pool is now 1.222 L (`venous_pool_volume_l` in `src/anesthesia_sim/data/patients/reference_adult.json`), not 1.0 L. At 5 L/min that gives the 14.7 s time constant that `docs/MODEL.md` states under "Parameter provenance", not 12 s. So the 55%, 34% and 17% shortfalls at 30, 60 and 120 s must be measured again before they are written down. The brief's "Where" names `app/simulation_view.py`, but its `touches:` names `app/dashboard_frame.py`.


**Done 2026-11-22.** Re-measured at the one-second step with the 1.222 L pool, the reference adult at its opening settings and a 1 MAC dial. The brief's 55%, 34% and 17% compared the trace with a fast-mixing run. This measurement compares it, in the same run, with the blood leaving the tissues at that moment (`tissue_return_partial_pressure_fraction`), which needs no second run. The mixed-venous value is 61% below that blood at 30 s, 38-40% at 1 minute, 18-20% at 2 minutes, 5% at 5 minutes and 1-2% at 10 minutes, with each of the three agents.

**The brief's premise did not hold, and the note says the opposite of what it expected.** Measured against the alveolar value, the pool's lag is small. It makes up 0.2-7.2% of the gap between the alveolar and the mixed-venous values over the first 5 minutes, at most for desflurane. At 1 minute the mixed-venous value is 7-8% of the alveolar, and the blood leaving the tissues is 11-14%. So a low early mixed-venous reading is mostly tissue uptake, and the pool only delays it slightly. A learner who reads the early trace as uptake is mostly right.

**Framing, checked at the source.** Mapleson 1963 (J Appl Physiol 18:197-204, Appendix 2, p. 204, read in full text from the private reference corpus on 2026-11-22) says that while concentrations rise the venous blood reaching the lungs is lower than the blood leaving the tissues, and that leaving the circulation time out matters only in the first minute or two after a change of inspired concentration. So the lag is the model's stand-in for venous transit, in the physiological direction, and not an artefact. Its shape differs from a real transit, which is a delay. Davis and Mapleson 1981 is not in the corpus, so it was not re-read; `docs/MODEL.md` cites only its p. 400 for the pool's volume, from the reading recorded in `PL-8ZJQ`.

**No interface cue: decided, not omitted.** The Mixed venous readout and trace gain no notice. The measurement shows that the early curve is mostly the uptake a learner would read into it, so a notice would warn against a reading that is largely correct. `.claude/rules/ui-reader.md` (project owner, 2026-09-05 and 2026-09-08) also puts a caveat about what the model does in `docs/MODEL.md` rather than on screen, and keeps standing text off the dashboard. This is the clearly correct option under that rule, so it is taken rather than asked.

`docs/MODEL.md` § "Venous blood" now says what the pool does in the first minutes, with these figures, and § "Known limitations" lists venous transit as not represented. `test_the_venous_pool_lag_in_the_first_minutes_is_small_beside_tissue_uptake` in `tests/unit/test_blood.py` computes the figures for each agent.

Docs checked: `docs/MODEL.md` (§ "Venous blood", § "The reference adult", § "Known limitations"), `docs/PARAMETERS.md` (its two mentions of the 14.7 s time constant agree), `docs/INTERFACE.md` and `docs/VERIFICATION.md` (no statement about the early mixed-venous curve), `README.md` (none).

**Blind review, 2026-11-22.** Both passes named the same two findings. First (should-fix, both passes): every figure was measured at 5.0 L/min, and the pool's time constant is its volume over the cardiac output, so a learner who lowers the output stretches the lag. Re-measured with each agent: at 2.0 L/min the mixed-venous value is 81% below the blood leaving the tissues at 30 s, 65-66% at 1 minute, 42-44% at 2 minutes, 15-16% at 5 minutes and 5% at 10 minutes; at 1.0 L/min it is still 31-32% below at 5 minutes and 13% at 10 minutes. `docs/MODEL.md` § "Venous blood" now gives the time constant at 5.0 and 2.0 L/min, ties the figures to 5.0 L/min, gives the 2.0 L/min figures, and says the least exact stretch lasts longer at a low output. The test now runs at both outputs. Second (optional, both passes): "never more than 7%" was below the measured 7.17% for desflurane at 5.0 L/min and 7.45% at 2.0 L/min. The sentence now says "at most about 7%", which the test's limit of 7.5% holds. The share stays at 5.7-7.5% at all three outputs, so the conclusion that a low early reading is mostly uptake holds at any output.
