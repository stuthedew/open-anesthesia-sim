---
id: PL-F2T2
title: SimulationView._remove_time_bookmark and _remove_mac_target read the reference run's snapshot outside any halt gate, so Remove in the marks dialog on a run whose snapshot refuses raises out of the slot as PL-V2HC's readers did
priority: P2
effort: S
status: ready
classes: defect, ux
feature: every-control-restates-the-halt
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-12
payoff: Remove in the marks dialog on a run that cannot be read ends in the halt on screen rather than a button that silently does nothing
verify: grep -q 'def test_removing_a_mark_on_a_run_whose_snapshot_refuses_restates_the_halt' tests/integration/test_simulation_view.py
---

**Problem.** SimulationView._remove_time_bookmark and _remove_mac_target read the reference run's snapshot outside any halt gate, so Remove in the marks dialog on a run whose snapshot refuses raises out of the slot as PL-V2HC's readers did

**Why it matters.** The two removers run inside a slot, from the marks dialog's
buttons, and read `self._runs[0].snapshot()` to find the selected mark before
`_apply_to_every_run` runs. On a run whose own snapshot refuses a value
(`PL-7DJK`) the read raises there, which the toolkit prints and swallows: the
button does nothing and nothing on screen says so, the stale-state failure
`PL-V2HC` closed for the agent selector and the sliders by reading the snapshot
through `RunView._snapshot_for_a_control`. No supported setting reaches a
refusing snapshot (`core/concentration.py`), so this is reachable only through
a future write that skips every checked path, as `PL-544D`'s was.

**What a fix probably wants.** The dashboard's counterpart of
`RunView._snapshot_for_a_control`: read the reference run's snapshot under the
guard `present` uses, halting every run through `_halt_every_run` on the raise,
so the removal is answered by the halt on screen. A test that makes the
snapshot refuse, as `test_an_agent_change_on_a_halted_run_restates_the_halt`
does, then clicks Remove.

**Found 2026-10-12** while building `PL-V2HC`, by reading
`src/anesthesia_sim/app/simulation_view.py`; not run, for the same reason
`PL-V2HC` recorded.

**Done when.** Clicking Remove in the marks dialog on a run whose snapshot
refuses ends in the halt on screen rather than a raise the toolkit prints,
shown by an integration test.
