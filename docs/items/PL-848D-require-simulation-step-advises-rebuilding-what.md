---
id: PL-848D
title: require_simulation_step advises rebuilding what it refuses from the same value - SimulationStep(0.1) for a CaseInstant(0.1) handed in as the step, which would build a 0.1 s step from an instant - and _require_built names only the three flows as swapped arguments; both print with repr, so an int past 4,300 digits raises ValueError instead of TypeError (measured 2026-10-04); bring both to the refusal require_case_instant and require_step_count use, _CHECKED_QUANTITIES and _shown (found folding #1354's review)
status: untriaged
feature: parse-dont-validate
added: 2026-10-04
---

**Problem.** require_simulation_step advises rebuilding what it refuses from the same value - SimulationStep(0.1) for a CaseInstant(0.1) handed in as the step, which would build a 0.1 s step from an instant - and _require_built names only the three flows as swapped arguments; both print with repr, so an int past 4,300 digits raises ValueError instead of TypeError (measured 2026-10-04); bring both to the refusal require_case_instant and require_step_count use, _CHECKED_QUANTITIES and _shown (found folding #1354's review)
