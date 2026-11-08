---
id: PL-624C
title: test_the_branch_is_drawn_beside_the_trunk_on_one_time_axis draws its own frame, so it cannot detect a fork that fails to redraw
priority: P2
effort: S
status: done
classes: defect, test
feature: branch-display-tests
milestone: v0.5.21
touches: tests/integration/test_simulation_view.py
added: 2026-09-20
closed: 2026-10-01
pr: 1260
payoff: makes a fork that adds a run without redrawing the chart fail a test, where today the test supplies the frame itself and cannot see it
verify: grep -q 'def test_taking_a_fork_redraws_the_chart_without_prompting' tests/integration/test_simulation_view.py
---

**Problem.** test_the_branch_is_drawn_beside_the_trunk_on_one_time_axis draws its own frame, so it cannot detect a fork that fails to redraw

**Found 2026-09-20** by the adversarial review of `#784`, and upheld against
refutation. `PL-VKJW` is what made two runs reachable from a shipped entry
point for the first time, so this is that change's to answer rather than a
pre-existing gap.

**Why it matters.** The test calls `_take_fork(view, 60.0)` and then
`view.present(False)` itself before reading `view._frame`. Prompting the redraw
is what makes the assertions unconditional: the frame it inspects is the one the
test asked for, so a fork that added a run without the display following would
produce exactly the same two-run frame and the test would still pass.

This is the shape the apparatus floor refuses and that `CLAUDE.md` names as
compounding friction - a check passing while the guarantee it stands for is
void - arriving in a product test rather than in a tool. Its docstring claims
"One frame, both runs, and the branch's curve begins where it was taken", and
the first clause of that is the part it cannot see.

**Verified 2026-09-20**: `tests/integration/test_simulation_view.py`, the body
of `test_the_branch_is_drawn_beside_the_trunk_on_one_time_axis`, holds
`view.present(False)` between the fork and the frame read.

**Distinguish it from `PL-FKN7`.** That one is that the
`presentation_requested` signal has no test at all, anywhere. This one is that a
test which *looks* like it covers the fork's redraw does not, and would go on
reading as coverage after `PL-FKN7` landed. Both are worth closing; the fix here
is to stop the test supplying its own frame, which makes the redraw a
precondition of the assertions it already makes.

**Done when.** Taking a fork is shown to redraw the chart without the test
prompting it, and the existing test no longer calls `view.present` between the
fork and the frame it reads - so a fork that fails to redraw fails a test.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2, because this milestone's own work created them", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood.

> - PL-624C (S) — **deferred 2026-09-21.** `test_the_branch_is_drawn_beside_the_trunk_on_one_time_axis` calls `view.present(False)` itself between the fork and the frame it reads, so the frame it inspects is the one it asked for and a fork that failed to redraw would still pass it. `defect`, `test`. A check passing while its guarantee is void is the shape this project treats as compounding friction, but the arithmetic that rule asks for does not carry here: it makes no other gate entry cheaper, and the capability it fails to cover is this milestone's own.
