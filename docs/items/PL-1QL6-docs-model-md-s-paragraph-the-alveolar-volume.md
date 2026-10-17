---
id: PL-1QL6
title: docs/MODEL.md's paragraph 'The alveolar volume is held constant, and that is what excludes nitrous oxide' (PL-L2F2) names core/alveolar.py's apply_blood_uptake as the code that holds the alveolar volume constant, but PL-GS5X removed that method with the operator split, so the sentence should name what implements the constant volume now (found in PL-19Y0's docs sweep)
priority: P2
effort: S
status: ready
classes: docs, defect
touches: docs/MODEL.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
payoff: docs/MODEL.md points a reader at the code that actually keeps the alveolar volume constant, so the assumption that excludes nitrous oxide can be checked against the source
verify: ! grep -qF 'apply_blood_uptake' docs/MODEL.md
---

**Problem.** docs/MODEL.md's paragraph 'The alveolar volume is held constant, and that is what excludes nitrous oxide' (PL-L2F2) names core/alveolar.py's apply_blood_uptake as the code that holds the alveolar volume constant, but PL-GS5X removed that method with the operator split, so the sentence should name what implements the constant volume now (found in PL-19Y0's docs sweep)

**Reproduced 2026-10-17.** `grep -n apply_blood_uptake docs/MODEL.md` finds the
name once, at the paragraph's second sentence. The only other mention in `src/`
is `core/alveolar.py`'s module docstring, which says the method existed and was
removed.

**Why it matters.** `docs/MODEL.md` is the authoritative specification of the
model. A reader who follows it to the code that keeps the alveolar volume
constant finds no such method, and cannot check the assumption that excludes
nitrous oxide.

**Done when.** The paragraph names the code that holds the alveolar volume
constant after the operator split, and no longer names `apply_blood_uptake`.
