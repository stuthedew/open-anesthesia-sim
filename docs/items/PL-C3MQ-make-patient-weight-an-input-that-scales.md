---
id: PL-C3MQ
title: Make patient weight an input that scales compartment volumes, blood flows and ventilation together by one sourced rule, within a sourced range
priority: P1
effort: L
status: blocked
classes: feature, science, safety
feature: patient-model
touches: src/anesthesia_sim/core, src/anesthesia_sim/data, src/anesthesia_sim/app, docs/MODEL.md, docs/PARAMETERS.md, tests
blocked-by: PL-PTYM
deferred-from: v0.7.0 - filed 2026-11-27 as v0.8.0's Required scope (PL-8NDZ), after Gate 3 froze. Not live: checked 2026-11-27 at 009da829, the tree has no patient age or weight input and no fifth compartment, so no displayed value is wrong until this work starts
added: 2026-11-27
payoff: a user sets the patient's weight and the whole body scales with it by one sourced rule
---

**Problem.** Make patient weight an input that scales compartment volumes, blood flows and ventilation together by one sourced rule, within a sourced range

**Why it matters.** `ROADMAP.md` § "v0.8.0 - the patient, on the five-compartment model", Required scope entry 8. Weight is what most changes
uptake between two adults of the same age. `PL-YKSM` showed that scaling only
the flows makes a light patient equilibrate more slowly, the wrong way round,
so volumes, flows, alveolar gas volume and ventilation move together or not at
all (planned-milestone item 30).

**Candidate rules, to be chosen from sources read in full:**

1. Davis and Mapleson distribute an individual's total mass, cardiac output or
   blood volume in the standard man's proportions (*Br J Anaesth*
   1981;53:399-405, p. 400, Table II, p. 402). Read in full.
2. Lerou and Booij give every volume as a fraction of body mass (*Br J Anaesth*
   2001;86:12-28, Tables 6 and 7, p. 26). Only those tables have been read.
   Read the paper in full before relying on it.

The weight range is sourced as well. Planned-milestone item 30 records that a
bound invented to have a bound is worse than none.

**Done when.** Weight scales volumes, flows and ventilation by one rule;
`docs/MODEL.md` states the rule and its range with sources read in full; the
limits on cardiac output and ventilation scale with it; and a weight outside
the range is refused with a notice that names the limit and the value.

**Generator check.** None: filed by the v0.8.0 scoping round (`PL-8NDZ`) from its approved scope, not by a finding.
