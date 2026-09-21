---
id: PL-RBMK
title: _apply_to_every_run documents a two-phase write it does not implement: it applies in a loop and catches, so the docstring promises atomicity the code cannot give
priority: P3
effort: S
status: ready
classes: defect
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
added: 2026-09-20
payoff: a reader of the write-to-every-run path is told what it actually guarantees, on the invariant the marks panel now halts the dashboard over
verify: grep -q 'computed against copies first' src/anesthesia_sim/app/simulation_view.py && exit 1 || exit 0
---

**Problem.** _apply_to_every_run documents a two-phase write it does not implement: it applies in a loop and catches, so the docstring promises atomicity the code cannot give

**Why it matters.** `SimulationView._apply_to_every_run`'s docstring says the
edits "are computed against copies first and written only once all of them
have been accepted". The code applies the edit to each run in a loop and
catches a refusal, so a run that accepts before a later run refuses keeps its
edit. The docstring is what a later reader relies on, and it describes a
guarantee the code does not provide.

It is inert today, and the reason is worth recording because it is what a
reader would have to re-derive: every `BookmarkSet` operation is a pure
function of the set and the mark, so with the runs' sets equal all runs accept
or all refuse at the same run, and the method is synchronous, so no render
tick or step timer interleaves between the two writes. The two-phase write
buys nothing *while the sets are equal* — and the docstring is the reason a
reader would believe the sets stay equal.

**`PL-LHBY` made that invariant load-bearing**, which is why this is worth an
item rather than a shrug. `bookmark_panel` now reads the reference run's mark
set and every displayed run's standings against it, so a divergence raises
`SimulationConfigurationError` out of `_refresh_bookmarks` and halts the whole
dashboard — reproduced by the adversarial review of that item by forcing a
branch's set apart. Before it, a divergence silently drew the trunk's
standing. Louder is the right direction, and it means the honesty of this
docstring now has a consequence.

**Found by** the adversarial review of `PL-LHBY`, which also fuzzed the
invariant: 40 trials of 120 randomized dashboard gestures each — adds,
removals, forks, resets of trunk and branch, runs to a halt, agent changes —
roughly 24,000 gestures, with every displayed run's `bookmarks` compared after
each. No mismatch and no halt. So this is a documentation defect and a latent
one, not a live bug.

**Done when.** The docstring describes what the loop does, or the loop does
what the docstring describes — and the choice is recorded either way.
