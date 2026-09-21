---
id: PL-FKN7
title: "The branch's presentation_requested wiring is untested: every branch test reads the controller, none reads the display"
priority: P2
effort: S
status: ready
classes: test
feature: branch-display-tests
touches: tests/integration/test_simulation_view.py
added: 2026-09-20
payoff: puts the only path a run's state reaches the display by under test, so a branch that freezes on screen while its controller advances is caught
verify: grep -q 'def test_a_runs_presentation_request_reaches_the_display' tests/integration/test_simulation_view.py
---

**Problem.** The branch's presentation_requested wiring is untested: every branch test reads the controller, none reads the display

**Found 2026-09-20** by the adversarial review of `#784`, and upheld against
refutation. `PL-VKJW` is what made two runs reachable from a shipped entry
point for the first time, so this is that change's to answer rather than a
pre-existing gap.

**Why it matters.** `RunView.presentation_requested` is the one path by which a
run's own state changes reach the display: `run_view.py` emits it from six
places, `SimulationView._place_run` connects it to `self.present`, and
`_remove_run` disconnects it. `grep -rc presentation_requested tests/` returns
nothing - the symbol does not occur anywhere under `tests/` - so every one of
those seven edges is unheld.

The consequence is specific to a branch rather than general. A run the dashboard
was built over gets its redraws through the construction path as well, so a
broken connection there would surface elsewhere; a branch placed an hour later
has only `_place_run`'s connect. A branch whose signal never reached `present`
would sit visibly frozen while its controller advanced correctly, and every
existing branch test - which reads `view.runs[n].controller` and
`view.runs[n].snapshot()` - would pass.

**Verified 2026-09-20**: `grep -rn presentation_requested src/anesthesia_sim/app`
gives eight occurrences across `run_view.py` and `simulation_view.py`;
`grep -rn presentation_requested tests/` gives none.

**Done when.** A test drives a run's `presentation_requested` and shows it
reaching `SimulationView.present`, and the disconnect in `_remove_run` is held
too - so a removed run's signal cannot write on widgets that have been deleted.
