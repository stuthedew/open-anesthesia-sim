---
id: PL-024
title: Document what the venous pool does to early mixed-venous readings
priority: P2
effort: S
status: ready
classes: docs, ux
touches: docs/MODEL.md, src/anesthesia_sim/app/simulation_view.py
added: 2026-08-24
---

**Problem.** The venous pool's mixing time constant — 60 · V/Q̇ = 12 s at the
reference 1.0 L and 5 L/min — dominates the displayed mixed-venous value
through the first minute of wash-in. Against a near-instant-mixing
comparison it reads 55% low at 30 s, 34% low at 60 s, and 17% low at 120 s.
Mixed venous is displayed both as a metric and as a chart trace, and neither
`docs/MODEL.md`'s "Known limitations" nor the interface says the early curve
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
