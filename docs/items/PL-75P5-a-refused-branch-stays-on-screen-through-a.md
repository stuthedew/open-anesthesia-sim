---
id: PL-75P5
title: A refused branch stays on screen through a trunk Reset on a one-run dashboard, because _handle_case_restarted returns before it clears _fork_refusal: the banner names an instant the reset run no longer holds
priority: P2
effort: S
status: done
classes: defect, ux
feature: reset-aftermath
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py, docs/items/PL-75P5-a-refused-branch-stays-on-screen-through-a.md, docs/items/PL-08SS-simulationview-handle-fork-and-handle-halt-fork.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-14QR's 2026-09-22 triage pass
added: 2026-09-22
closed: 2026-10-17
pr: 1476
payoff: a learner who resets after a refused branch stops seeing a refusal that names an instant the restarted case no longer holds
verify: grep -q 'def test_a_refused_branch_does_not_survive_a_one_run_reset' tests/integration/test_simulation_view.py
recurrences: 2026-10-12 PL-08SS withdrawn 2026-10-17 PL-75P5, 2026-10-12 PL-MMNX withdrawn 2026-10-17 PL-75P5
---

**Problem.** A refused branch stays on screen through a trunk Reset on a one-run dashboard, because _handle_case_restarted returns before it clears _fork_refusal: the banner names an instant the reset run no longer holds

**Found 2026-09-22** while working `PL-WG73` (the comparison lock naming a
control that does not exist), and **reproduced** against real widgets under the
offscreen platform before being filed.

**Why it matters.** `SimulationView._handle_case_restarted` clears
`_fork_refusal` at its last line, but it returns at its first guard - `if
self._case is None or len(self._runs) == 1` - whenever the dashboard is drawing
one run. That guard is `PL-LQ19`'s and is correct for what it was written for:
a one-run dashboard has no branch to drop. Clearing the refusal was put inside
it by position rather than by argument, and a refusal is not a branch.

So on the ordinary single-run case - which is every case before a learner
branches - a refused `Branch here` press leaves its banner standing through the
Reset that answers it. The run has restarted at induction and holds one
keyframe; the banner still reports an instant that run no longer has.
`.claude/rules/expert-review.md` names stale UI state directly, and this is the
detectable-only-against-a-remembered-list kind: nothing on the panel says the
sentence is older than the case under it.

**Reproduction** (offscreen, `tests/integration/test_simulation_view.py`'s own
helpers): build `_case_view` on `_branched_case()`, make `case.fork_at` raise
`SimulationConfigurationError`, click `take_button`, then click
`runs[0]._reset_button`. The panel's notice reads `Setting refused - no such
instant in this case` before the Reset and after it, and `_fork_refusal` holds
the same string.

**On the fix.** Clearing `_fork_refusal` before the guard is the whole of the
behavior change; the judgment is whether anything else below that guard is
there by position too. `RunView._handle_reset` already clears its own
`_rejected_setting_notice`, which is the same rule one layer down and the
precedent to read.

**Done when.** A refused branch does not survive the Reset that follows it on a
one-run dashboard, and a test in `tests/integration/test_simulation_view.py`
holds it.

**Premise re-read 2026-09-22 (`PL-14QR`, triage).** `_handle_case_restarted` still returns at
`if self._case is None or len(self._runs) == 1:`, which comes before its
`self._fork_refusal = None`. The order the brief describes stands.

**Re-confirmed and fixed 2026-10-17.** The guard still stood as the re-read
above found it. The judgment the brief asked for came back with one more step
there by position: the case rebuild. `BranchedCase(trunk)` answers to the run
that ended, as the refusal does, and the `case` property's docstring already
says the case is replaced whenever the trunk starts over - yet with one run on
screen it was skipped, so a branch the case kept without drawing (`PL-08SS`'s
fork) outlived the Reset. `_handle_case_restarted` now returns early only for a
dashboard with no case; it rebuilds the case and clears `_fork_refusal` on every
trunk Reset, and only the layout work - dropping runs, restacking, renaming -
waits for a second run. The refusal test is the one `verify:` names and goes
through a real refusal, an offered instant with no keyframe, rather than a
patched `fork_at`. A second test,
`test_a_one_run_reset_leaves_a_case_with_no_branches`, holds the rebuild. Both
failed on the old guard and pass on the new one. `RunView` needed no change, and
`docs/MODEL.md` makes no statement about what a trunk Reset does to the fork
panel, so neither file moved. Rebuilding the case on a one-run Reset goes
past the refusal the brief named (project owner, 2026-10-17, ratified, over
clearing only the refusal).

**The two recurrence matches are withdrawn: neither is this mechanism filed
again.** `PL-MMNX` is `_halt_every_run` not restating a halt on the fork panel,
which is the `every-control-restates-the-halt` group's mechanism and shares
nothing with this guard but the panel. `PL-08SS`'s own defect is ordering -
the case keeping a branch before `add_run` has read the snapshot that draws it -
and that is still open. It met this guard only in its Reset half, which the
case rebuild above closes. Two items touching one guard is below the generator
count in any case, so nothing is recorded as `root-cause-of:`.
