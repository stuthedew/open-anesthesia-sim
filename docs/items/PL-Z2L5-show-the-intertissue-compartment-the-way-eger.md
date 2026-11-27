---
id: PL-Z2L5
title: Show the intertissue compartment the way Eger and Saidman draw it, and label its tension and amount apart from bulk fat
priority: P1
effort: M
status: blocked
classes: feature, safety
feature: patient-model
touches: src/anesthesia_sim/app, docs/INTERFACE.md
blocked-by: PL-PTYM
deferred-from: v0.7.0 - filed 2026-11-27 as v0.8.0's Required scope (PL-8NDZ), after Gate 3 froze. Not live: checked 2026-11-27 at 009da829, the tree has no patient age or weight input and no fifth compartment, so no displayed value is wrong until this work starts
added: 2026-11-27
payoff: a user sees the fast-filling intertissue layer apart from bulk fat, as the published teaching figures draw it
---

**Problem.** Show the intertissue compartment the way Eger and Saidman draw it, and label its tension and amount apart from bulk fat

**Why it matters.** `ROADMAP.md` § "v0.8.0 - the patient, on the five-compartment model", Required scope entry 4. The intertissue compartment
fills about five times faster than bulk fat: its time constants are 230, 412
and 396 minutes for desflurane, sevoflurane and isoflurane, against 1,226,
2,198 and 2,114 for fat (Eger and Saidman 2005, Table 3, p. 1024). Shown as
part of fat, its tension and amount would mislead a user about where the agent
is.

**What is settled.** Eger and Saidman draw the intertissue compartment as a
distinct layer at the edge of the fat group, filled from the vessel-rich and
muscle groups beside it (Figures 4 and 5, pp. 1023-1025). The schematic follows
that drawing (project owner, 2026-11-27: display follows best practice).

**What is left to decide.** How the concentration chart and the readouts show
it, decided from the closest published sources, ranked as
`.claude/rules/expert-review.md` § "Search the closest analog first" requires,
and recorded here with them.

**Done when.** The schematic draws the intertissue compartment as Eger and
Saidman do; its tension and amount are labelled separately from bulk fat
everywhere they appear; and `docs/INTERFACE.md` states the requirement with the
test that checks it.

**Generator check.** None: filed by the v0.8.0 scoping round (`PL-8NDZ`) from its approved scope, not by a finding.
