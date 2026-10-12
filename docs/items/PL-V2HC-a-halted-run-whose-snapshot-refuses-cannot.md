---
id: PL-V2HC
title: A halted run whose snapshot refuses cannot change agent: RunView._handle_agent_change and SimulationController.set_agent both read snapshot() while the selector is unlocked on a halted run, so the slot's raise is printed by Qt and the new-case dialog never opens; Reset is the one exit and the halt banner names it (found at PL-7DJK)
priority: P1
effort: M
status: done
classes: safety, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/controller.py, docs/ARCHITECTURE.md, docs/MODEL.md, tests/integration/test_simulation_view.py, tests/integration/test_controller.py
added: 2026-10-11
closed: 2026-10-12
pr: 1428
payoff: a control used on a halted run answers with the halt already on screen, never by silently doing nothing
verify: grep -q 'def test_an_agent_change_on_a_halted_run_restates_the_halt' tests/integration/test_simulation_view.py
---

**Problem.** A halted run whose snapshot refuses cannot change agent: RunView._handle_agent_change and SimulationController.set_agent both read snapshot() while the selector is unlocked on a halted run, so the slot's raise is printed by Qt and the new-case dialog never opens; Reset is the one exit and the halt banner names it (found at PL-7DJK)

**Problem.** Three readers of `RunView.snapshot()` sit outside the halt gate
and run on a halted run: `_handle_agent_change` reads it first (and
`SimulationController.set_agent` reads it again), `_refresh_against_last_frame`
reads it after `_apply_setting`'s `try` has returned, and the selector is
unlocked on a halted run, since `transport` locks it only while running, on
a branch or while comparing. On a run halted because its own snapshot refuses
a value (`PL-7DJK`), picking an agent or dragging a slider raises inside the
slot, which Qt prints and swallows: the new-case dialog never opens and
nothing on screen changes, with no notice. Reset reads no snapshot and is the
exit the halt banner names. No supported setting reaches a refusing snapshot
(`core/concentration.py`), so this is reachable only by a future write that
skips every checked path, as `PL-544D` describes.

**What a fix probably wants.** Either route both readers through
`_apply_setting`'s gate, so the raise becomes the halt it already is and
`present_halt` restates it, or lock the selector and the sliders on a halted
run - a user-facing choice, since a halted run's sliders are usable today.
Put that choice to the owner before building the second.

**Confirmed 2026-10-11** on `main` at `16a20a4f` by reading: `RunView._handle_agent_change`
(`app/run_view.py`) calls `self.snapshot()` as its first statement, outside
`_apply_setting`'s gate. Not run: no supported setting reaches a refusing
snapshot, so a run needs `PL-544D`'s write or a patched `snapshot` to show it.

**Why it matters.** A control that accepts a choice and then does nothing, with
no notice, is the stale-state failure `CLAUDE.md`'s safety standard names: the
learner is left looking at a screen that no longer reflects what they asked for.
`PL-544D` closing the one known route does not make this moot, since any future
refusing snapshot reaches the same three readers.

**Recommended route, taken at triage 2026-10-11.** The first in the brief: route
the readers through `_apply_setting`'s gate, so the raise becomes the halt it
already is and `present_halt` restates it. Locking the selector and sliders on a
halted run changes what a learner can touch and is the owner's call; it is not
part of this item.

**Done when.** Picking an agent or moving a slider on a run halted by a refusing
snapshot ends in the halt already on screen rather than a raise Qt prints, shown
by an integration test that makes `snapshot` refuse.
