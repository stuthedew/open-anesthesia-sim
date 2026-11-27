---
id: PL-XXWY
title: Re-run the wash-in, elimination and 24-hour washout comparisons with measured human data on the five-compartment model, beside the four-compartment results, and check the new equations against an independent calculation
priority: P1
effort: M
status: blocked
classes: science
feature: patient-model
touches: tests/reference, docs/VERIFICATION.md
blocked-by: PL-PTYM
deferred-from: v0.7.0 - filed 2026-11-27 as v0.8.0's Required scope (PL-8NDZ), after Gate 3 froze. Not live: checked 2026-11-27 at 009da829, the tree has no patient age or weight input and no fifth compartment, so no displayed value is wrong until this work starts
added: 2026-11-27
payoff: the new model's wash-in, elimination and 24-hour washout are checked against measured human data and an independent calculation
---

**Problem.** Re-run the wash-in, elimination and 24-hour washout comparisons with measured human data on the five-compartment model, beside the four-compartment results, and check the new equations against an independent calculation

**Why it matters.** `ROADMAP.md` § "v0.8.0 - the patient, on the five-compartment model", Required scope entry 3. A changed model has to be
checked against measured human data again, and the late washout is the curve
the fifth compartment exists to fit. The comparisons today are wash-in at 30
minutes, elimination at 5 minutes, and the first 24 hours of elimination
against Yasuda's mean curves (`PL-KK1Q`). Each one checks the published curve,
not the equations, so the new equations also need an independent reference
calculation.

**Done when.** All three comparisons are re-run on the five-compartment model,
and each result is recorded beside the four-compartment result as agreeing or
not; and a test checks the new equations against an independently calculated
reference.

**Generator check.** None: filed by the v0.8.0 scoping round (`PL-8NDZ`) from its approved scope, not by a finding.
