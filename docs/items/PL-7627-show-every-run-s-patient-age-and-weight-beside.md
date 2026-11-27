---
id: PL-7627
title: Show every run's patient age and weight beside it, on both runs of a comparison, and test patient inputs through to the displayed MAC
priority: P1
effort: M
status: blocked
classes: feature, safety
feature: patient-model
touches: src/anesthesia_sim/app, docs/INTERFACE.md, tests
blocked-by: PL-R8JK, PL-C3MQ
deferred-from: v0.7.0 - filed 2026-11-27 as v0.8.0's Required scope (PL-8NDZ), after Gate 3 froze. Not live: checked 2026-11-27 at 009da829, the tree has no patient age or weight input and no fifth compartment, so no displayed value is wrong until this work starts
added: 2026-11-27
payoff: no two curves are compared without each run's patient on screen
---

**Problem.** Show every run's patient age and weight beside it, on both runs of a comparison, and test patient inputs through to the displayed MAC

**Why it matters.** `ROADMAP.md` § "v0.8.0 - the patient, on the five-compartment model", Required scope entry 9. Once two runs can be for
different patients, a comparison that does not show each run's patient invites
a user to read a difference in patient as a difference in technique. The
safety standard also asks for an end-to-end test from patient inputs to the
displayed value.

**Done when.** Each run shows its patient's age and weight wherever the run is
shown, including both runs in a comparison; and a test runs patient inputs
through model selection, calculation, units and formatting to the displayed
MAC.

**Generator check.** None: filed by the v0.8.0 scoping round (`PL-8NDZ`) from its approved scope, not by a finding.
