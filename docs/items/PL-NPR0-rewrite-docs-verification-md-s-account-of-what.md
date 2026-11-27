---
id: PL-NPR0
title: Rewrite docs/VERIFICATION.md's account of what keeps a real patient's data out of a run, now that age and weight are inputs
priority: P1
effort: S
status: blocked
classes: docs, safety
feature: patient-model
touches: docs/VERIFICATION.md
blocked-by: PL-R8JK, PL-C3MQ
deferred-from: v0.7.0 - filed 2026-11-27 as v0.8.0's Required scope (PL-8NDZ), after Gate 3 froze. Not live: checked 2026-11-27 at 009da829, the tree has no patient age or weight input and no fifth compartment, so no displayed value is wrong until this work starts
added: 2026-11-27
payoff: the verification document names the safeguards that still hold once a run can be built from a real patient's data
---

**Problem.** Rewrite docs/VERIFICATION.md's account of what keeps a real patient's data out of a run, now that age and weight are inputs

**Why it matters.** `ROADMAP.md` § "v0.8.0 - the patient, on the five-compartment model", Required scope entry 10. `docs/VERIFICATION.md` §
"What keeps a real patient's data out of a run" names two safeguards, and the
fixed reference adult is one of them (`PL-DXJR`). Once age and weight are
inputs, a run can be built from a real patient's data, so that safeguard is
gone and the section would describe a protection that no longer exists.

**Done when.** The section and its hazard row describe the safeguards that hold
with age and weight as inputs, and name the test that checks each.

**Generator check.** None: filed by the v0.8.0 scoping round (`PL-8NDZ`) from its approved scope, not by a finding.
