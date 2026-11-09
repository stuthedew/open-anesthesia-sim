---
id: PL-RBMK
title: _apply_to_every_run documents a two-phase write it does not implement: it applies in a loop and catches, so the docstring promises atomicity the code cannot give
priority: P3
effort: S
status: done
classes: defect
milestone: v0.5.24
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
added: 2026-09-20
closed: 2026-10-12
pr: 1428
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

**Decision, 2026-10-12** (a session's call, there being one clearly correct
option). The docstring now describes the loop: run by run, stopping at the
first refusal, with no second phase, and why that is all-or-none while the
displayed runs' sets are equal - every `BookmarkSet` operation is a pure
function of the set and the mark, so the first run refuses before any has
changed - with `_refresh_bookmarks` halting the dashboard on the frame the
sets diverge (`PL-LHBY`). The two-phase write was not built: it would guard an
invariant the frame already refuses louder, every bookmark method on
`SimulationController` delegates to a pure `BookmarkSet` operation (read
2026-10-12), and the fuzz recorded above found no divergence - its own
arithmetic, 40 trials of 120 gestures, gives 4,800 rather than the roughly
24,000 it states, so the code quotes neither figure (found at review). The
phrase the `verify:` command greps for is gone with the paragraph that carried
it.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground".

> **`PL-RBMK` is a third from the same close-out and declines on the refilling-queue ground instead**, because its problem predates the freeze rather than being new. `SimulationView._apply_to_every_run` has always documented a two-phase write that it does not implement. The gap is inert. Every `BookmarkSet` operation is a pure function of the set and the mark. So while the runs' sets are equal, all runs accept or all refuse at the same run. The same review fuzzed that invariant over roughly 24,000 randomized dashboard gestures and found no mismatch. Only the consequence of a break has changed. `PL-LHBY` made the panel read every run's standings against the reference run's set. So a divergence now halts the dashboard instead of quietly drawing the trunk's answer. So `PL-RBMK` concerns a docstring that nobody can act on wrongly today, guarding an invariant that now has teeth.
