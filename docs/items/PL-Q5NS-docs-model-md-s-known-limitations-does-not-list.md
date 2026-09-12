---
id: PL-Q5NS
title: docs/MODEL.md's Known limitations does not list lung tissue and pulmonary blood as an omitted store, which is worth about 20 percent of every agent's fast pool
priority: P1
effort: S
status: ready
classes: science, docs
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-08
verify: python3 tools/doc_check.py check && grep -q 'lung tissue and pulmonary blood' docs/MODEL.md
---

**Problem.** docs/MODEL.md's Known limitations does not list lung tissue and pulmonary blood as an omitted store, which is worth about 20 percent of every agent's fast pool

**Problem, stated fully.** The list under "Known limitations" names a separate
arterial blood-mixing compartment, multiple alveolar units, dead space and
airway sampling delay, but not the lung's own tissue and pulmonary blood,
which this model has no compartment for either. Measured while working
`PL-73G7`: on round physiologic figures - 1 kg of lung tissue at a tissue:blood
ratio of 1.2, and 1.8 L of pulmonary and arterial blood - that store is worth
20.1% of desflurane's fast pool, 19.7% of sevoflurane's and 23.4% of
isoflurane's. It is fully equilibrated at 30 minutes, so it is invisible in
`F_A/F_I` and shows up only in an elimination, which is why nothing before the
open-circuit diagnostic would have surfaced it.

**Why it matters.** The list is where a reader goes to find out what this model
leaves out, and an omission of that size reading as absent from the list is the
same failure the list exists to prevent. It is also now cited from
"Desflurane's residual, and why the parameter file was not changed", which
measures the term - so the document names it in one place and not in the place
a reader looks for it.

**Where.** `docs/MODEL.md` "Known limitations".

**Done when.** The list names it, and says whether the figures above belong
with it or stay where they are measured.
