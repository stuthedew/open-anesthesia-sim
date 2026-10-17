---
id: PL-MMNX
title: While frames keep failing on a paused trunk, the Branch here button stays live over the failed run: _halt_every_run restates the halt on each RunView but not on the fork panel, and a press is refused with the refusal swallowed by the next failing frame
priority: P2
effort: S
status: done
classes: defect, ux
feature: every-control-restates-the-halt
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-12
closed: 2026-10-17
pr: 1492
payoff: a paused trunk whose frames fail stops offering Branch here, so the fork panel no longer invites a branch the case will refuse beside a run every other control says has failed
verify: grep -q 'def test_a_failing_frame_on_a_paused_trunk_withdraws_branch_here' tests/integration/test_simulation_view.py
recurrences: 2026-10-17 PL-YHR3
---

**Problem.** While frames keep failing on a paused trunk, the Branch here button stays live over the failed run: _halt_every_run restates the halt on each RunView but not on the fork panel, and a press is refused with the refusal swallowed by the next failing frame

**Found by the adversarial review of `PL-Y2SL`** (2026-10-12), reproduced
offscreen: with every frame failing, the trunk read "Stopped - simulation
error" with Start and Pause disabled, while the fork panel still showed a live
"Branch here: 1m"; a press added no run and the refusal never reached the
notice, because `present(False)` after it raised again. Before `PL-Y2SL` this
reached only a trunk standing on a halt; the button is now offered at every
pause, so any paused trunk whose frames keep failing shows it. The fork panel
is one more control `_halt_every_run` does not restate, the group this item is
filed under.

**Reproduced again 2026-10-17 at triage**, on this tree (`b9b3c812`), offscreen,
with a scratch script: a case whose trunk is paused at 60 s with a setting
change recorded, every frame then made to fail by replacing
`simulation_view.assemble_chart_frame` with one that raises. After the failing
`present(False)` the trunk read "Stopped — simulation error" with Start and
Pause disabled, while `here_button` stayed visible and enabled reading "Branch
here: 1m"; `BranchedCase.here_fork_point` already answered `None`. A press
added no run and set `_fork_refusal` to `fork_here`'s refusal ("this run
stopped at 60.0 s on a failure, not a pause ..."), and the only visible notice
was the halt banner, because the `present(False)` after the refusal raised
again. The mechanism is in the source: `_refresh_fork_panel` is called only
from the end of `_refresh_view`, which is what fails, and `_halt_every_run`
restates the halt through `RunView.present_halt` alone.

**Reachable only through a render-path raise**, which no supported setting
produces today - two runs come to be on different agents, or a snapshot whose
own values refuse (`PL-7DJK`) - so this is latent in the way its siblings
`PL-F2T2` and `PL-08SS` are, and banded with them at `P2`.

**Why it matters.** A control offered over a run every other widget says has
failed is the stale-state presentation this feature exists to remove: the
button invites a branch the case will refuse, and the refusal, which is the
one thing that would tell the learner why, is never shown. It also leaves the
fork panel as the one part of the screen still describing the run as it stood
before the failure.

**Not part of this item, noted for the work:** in the same reproduction the
keyframe selector's Branch button also stayed live, and a press there *did*
open a branch (runs 1 to 2, no refusal), since `fork_at` opens a branch from a
failed trunk's keyframe; the new run is then halted by the next failing frame.
Whether that is right is outside this item's question, which is only that the
panel state what the case would answer.

**Done when.** `SimulationView._halt_every_run` restates the halt on the fork
panel as well as on every run, from the case's own answers and before the frame
is attempted, so a failing frame on a paused trunk withdraws "Branch here"
(the panel drawn from `here_fork_point`, which is `None` then) without needing
a frame that draws; the restatement cannot itself raise out of the halt path.
A regression test in `tests/integration/test_simulation_view.py`,
`test_a_failing_frame_on_a_paused_trunk_withdraws_branch_here`, makes every
frame fail on a paused case and asserts `here_button` is hidden afterwards.

**Fixed 2026-10-17 under `PL-X7D5`'s second pull request.** `_halt_every_run`
calls `SimulationView._restate_fork_panel` after every run's `present_halt`.
It redraws the fork panel through `_refresh_fork_panel`, from the case's own
answers, so "Branch here" is withdrawn on a failed trunk, where
`here_fork_point` is `None`. Where those answers raise inside the halt path,
the panel offers nothing rather than the last frame's offer. The regression
test `test_a_failing_frame_on_a_paused_trunk_withdraws_branch_here` asserts
`here_button` is hidden, and
`test_a_fork_panel_the_case_cannot_restate_on_a_halt_offers_nothing` holds
the guard. The keyframe selector's Branch button, noted above as outside this
item, is unchanged by it. The bookmark panel has the same gap one panel over;
it is `PL-YHR3`.
