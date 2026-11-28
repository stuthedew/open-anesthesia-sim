---
id: PL-PTYM
title: Build the five-compartment model in core/, with the agent conserved across every compartment
priority: P1
effort: L
status: blocked
classes: science, feature
feature: patient-model
touches: src/anesthesia_sim/core, src/anesthesia_sim/data, tests
blocked-by: PL-5PNY
deferred-from: v0.7.0 - filed 2026-11-27 as v0.8.0's Required scope (PL-8NDZ), after Gate 3 froze. Not live: checked 2026-11-27 at 009da829, the tree has no patient age or weight input and no fifth compartment, so no displayed value is wrong until this work starts
added: 2026-11-27
payoff: the simulator computes Eger's five-compartment model, with fat's fast intertissue layer, and conserves the agent
---

**Problem.** Build the five-compartment model in core/, with the agent conserved across every compartment

**Why it matters.** `ROADMAP.md` § "v0.8.0 - the patient, on the five-compartment model", Required scope entry 2. The model a user sees is
whatever `core/` computes, so the specification in `PL-5PNY` changes nothing
until it is built. Agent conservation is a release gate under the development
rules, and a fifth compartment is a new place for agent to go missing.

**Done when.** `core/` computes the intertissue compartment and the larger lung
store as `docs/MODEL.md` specifies them, and a test checks that the amount of
agent is conserved across all compartments, to the precision the existing
conservation tests use.

**Generator check.** None: filed by the v0.8.0 scoping round (`PL-8NDZ`) from its approved scope, not by a finding.
