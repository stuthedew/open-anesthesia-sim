---
id: PL-V2HC
title: A halted run whose snapshot refuses cannot change agent: RunView._handle_agent_change and SimulationController.set_agent both read snapshot() while the selector is unlocked on a halted run, so the slot's raise is printed by Qt and the new-case dialog never opens; Reset is the one exit and the halt banner names it (found at PL-7DJK)
status: untriaged
added: 2026-10-11
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
