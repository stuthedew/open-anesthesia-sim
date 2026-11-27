---
id: PL-8K1F
title: Rewrite docs/MODEL.md's Known limitations for the five-compartment model
priority: P1
effort: S
status: blocked
classes: science, docs
feature: patient-model
touches: docs/MODEL.md
blocked-by: PL-XXWY
deferred-from: v0.7.0 - filed 2026-11-27 as v0.8.0's Required scope (PL-8NDZ), after Gate 3 froze. Not live: checked 2026-11-27 at 009da829, the tree has no patient age or weight input and no fifth compartment, so no displayed value is wrong until this work starts
added: 2026-11-27
payoff: docs/MODEL.md's limitations describe the model that ships, not the one it replaced
---

**Problem.** Rewrite docs/MODEL.md's Known limitations for the five-compartment model

**Why it matters.** `ROADMAP.md` § "v0.8.0 - the patient, on the five-compartment model", Required scope entry 5. `docs/MODEL.md` § "Known
limitations" describes what leaving out the fifth compartment costs, and how
the lung store is sized from round numbers with no source. Both become false
once the five-compartment model ships, and a clinician who trusts a stale
limitation can misread a correct value.

**Done when.** Known limitations states what the five-compartment model still
leaves out, and no sentence describes the four-compartment model as current.

**Generator check.** None: filed by the v0.8.0 scoping round (`PL-8NDZ`) from its approved scope, not by a finding.
