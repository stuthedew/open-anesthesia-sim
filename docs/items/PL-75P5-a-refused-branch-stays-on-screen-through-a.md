---
id: PL-75P5
title: A refused branch stays on screen through a trunk Reset on a one-run dashboard, because _handle_case_restarted returns before it clears _fork_refusal: the banner names an instant the reset run no longer holds
status: untriaged
feature: reset-aftermath
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/run_view.py, docs/MODEL.md, tests/integration/test_simulation_view.py
added: 2026-09-22
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
