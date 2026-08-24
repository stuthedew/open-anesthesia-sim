---
id: PL-026
title: Decide what the interface shows after a halted step
priority: P1
effort: S
status: needs-decision
classes: safety, ux
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/core/respiratory_system.py
added: 2026-08-24
---

**Problem.** PL-018 made a failed step halt the run, label it "Stopped —
simulation error", and warn that "the values shown may not reflect a
completed step". The compartment metrics and chart traces themselves are
still drawn, at whatever value the abandoned step left them. The step is
not transactional: `RespiratorySystem.advance()` applies its five
sub-exchanges in sequence and a guard can reject the fifth after the first
four have already mutated state.
**Why it matters.** `CLAUDE.md` prefers an obvious failure state to a
plausible-looking number when correctness cannot be established, and a
partially applied step is exactly that case. The banner is a warning after
the fact rather than an interface that prevents the misreading. Against
that: the numbers are also the most direct evidence of where the model
broke down, which has teaching value, and the run cannot be resumed from
them.
**Where.** `app/simulation_view.py` (`_refresh_view`, `_refresh_notice`),
`core/respiratory_system.py` (`advance`, `_advance_step`).
**Decision needed.** Three options, in increasing cost: keep the banner as
the only cue; blank or grey the metrics and freeze the chart at the last
completed step; or make the step transactional so a failure leaves the last
completed state intact and nothing is partial. The third removes the
question entirely but means capturing and restoring six compartments plus
the accounting validator on every step.
**Done when.** What a halted run displays is a recorded decision with its
reasoning, and `docs/MODEL.md`'s interface rules state it.
