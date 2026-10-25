---
id: PL-3HT2
title: A docstring in core/uptake_system.py still says a tissue's blood flow can be set directly, though #1537 removed that setter (found by PL-GTHP's checker on #376, 2026-10-25)
priority: P2
effort: S
status: ready
classes: defect
feature: replay-findings
touches: src/anesthesia_sim/core/uptake_system.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-10-25
payoff: a reader of AgentUptakeSystem.advance learns that no guarded write can make the tissue flows miss the cardiac output, so the refusal it restates is a safeguard
verify: ! grep -qF "Setting a tissue's blood flow directly on the" src/anesthesia_sim/core/uptake_system.py
---

**Problem.** A docstring in core/uptake_system.py still says a tissue's blood flow can be set directly, though #1537 removed that setter (found by PL-GTHP's checker on #376, 2026-10-25)

**Reproduced 2026-10-25.** On `main` at `e70e8421`, the docstring of
`AgentUptakeSystem.advance` says "Setting a tissue's blood flow directly on
the tissue can leave the flows that way (`PL-HQF5`)", meaning flows that no
longer sum to the cardiac output. `TissueGroup` has no flow setter. Each flow
is the tissue's perfusion fraction of the patient's cardiac output
(`TissueGroup.blood_flow_l_min_at`), and `Patient` refuses fractions that do
not sum to 1 and a second write of a fraction (`PL-Z0HN`). The tests that
reach the refusal write the fractions past their guard, as
`tests/unit/test_uptake_system_failure.py` says.

**Why it matters.** This paragraph explains why `advance` restates a settings
record it cannot build as a halted step. A reader told that an ordinary setter
produces the mismatch will look for a path the code no longer has, and will
misjudge how likely the halt is.

**Done when.** The paragraph says that no guarded write can make the tissue
flows miss the cardiac output, so the refusal is a safeguard, and it still
says why the failure is restated as a halt. No behaviour changes.
