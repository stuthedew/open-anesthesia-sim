---
id: PL-7DMJ
title: docs/MODEL.md names water vapour nowhere: alveolar gas is saturated at 47 mmHg, so a dry inspired fraction is diluted 6.2 percent on reaching the alveoli, and neither Assumptions nor Known limitations records the omission
priority: P1
effort: S
status: ready
classes: science, docs
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-17
verify: grep -qi 'water vapour' docs/MODEL.md
---

**Problem.** docs/MODEL.md names water vapour nowhere: alveolar gas is saturated at 47 mmHg, so a dry inspired fraction is diluted 6.2 percent on reaching the alveoli, and neither Assumptions nor Known limitations records the omission

**Found 2026-09-17, while working `PL-S6WW`** (the reference temperature the
agent-amount unit is stated at). Searching `docs/MODEL.md` for the gas-phase
conditions it does and does not carry returned nothing for *humid*, *water
vapour*, *saturated*, *BTPS*, *ATPS* or *dry gas* — the terms are absent from
the document entirely, not merely from "Known limitations".

**The physics.** Alveolar gas is fully saturated with water vapour at body
temperature, whose partial pressure is 47 mmHg. Agent arriving from the
circuit is dry. So an agent fraction $`F_I`$ of dry circuit gas, warmed and
humidified on reaching the alveoli, occupies a partial pressure of
$`F_I \times (760 - 47)`$ mmHg rather than $`F_I \times 760`$ — a dilution of
47/760, or 6.2 %, before any uptake has occurred. The model's alveolar
equation carries $`\dot V_A(F_I - F_A)`$ with no such factor, so it treats
$`F_I`$ as reaching the alveoli undiluted.

**Why it matters, and why it is a documentation finding rather than obviously
a defect.** Gas Man,
this project's reference implementation, makes the same simplification, and
the partition coefficients are ratios against a gas phase whose own water
content the measurements do not carry into this model either — so changing the
equation would move this model away from the trajectories its parameter set
was assembled for. What is wrong today is narrower and certain: the
simplification is made and is recorded nowhere, while nine smaller ones are
listed. A reader sizing the model against a real circle system cannot see it.

**Scope.** Decide whether this is an "Assumptions" line, a "Known limitations"
bullet with a note, or both, and write it. Changing the alveolar equation is
*not* in scope and should not be attempted from this item — if the reading
comes out that way, it is a roadmap question about the gas-phase model, beside
the single-condition assumption `PL-S6WW` recorded.

**Done when** `docs/MODEL.md` states that inspired gas is treated as reaching
the alveoli undiluted by water vapour, sizes the omission at 47/760, and says
why the model makes it.
