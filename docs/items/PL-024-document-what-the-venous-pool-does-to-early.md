---
id: PL-024
title: Document what the venous pool does to early mixed-venous readings
priority: P2
effort: S
status: ready
classes: docs, ux
feature: chart-readout
touches: docs/MODEL.md, src/anesthesia_sim/app/dashboard_frame.py
added: 2026-08-24
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
