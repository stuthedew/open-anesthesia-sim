---
id: PL-QRD1
title: A dashboard showing two runs lets either selector switch its own agent, which the shared MAC axis then refuses only after the controller has switched: lock the selectors while two runs are shown, with PL-8PSW
priority: P3
effort: S
status: blocked
classes: defect, ux
feature: scenario-branching
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py
blocked-by: PL-8PSW
added: 2026-09-15
---

**Problem.** A dashboard showing two runs lets either selector switch its own agent, which the shared MAC axis then refuses only after the controller has switched: lock the selectors while two runs are shown, with PL-8PSW

**Found by the Qt-correctness review of `PL-25KS`, 2026-09-15.** `RunView`
keeps its own agent selector, and `SimulationView` admits two runs. Switching
one run's agent goes through `SimulationController.set_agent`, which succeeds
on a trunk, and the refusal comes a moment later from `assemble_chart_frame`
(two agents cannot share one MAC axis) - after the controller has already
switched. `_halt_every_run` then fails both runs. The port made the halt
itself visible (`present_halt` writes each run's status word and banner with
no frame), but the switch should be refused before it reaches the controller:
while two runs are shown the selectors are locked, in the same disabled-and-
hidden form the running-agent chip uses, because a comparison is of one
agent by construction. Only reachable today by constructing a two-trunk
dashboard, which no shipped entry point does; `PL-8PSW` (overlay two branches)
is where two runs first reach a reader, and a branch's `set_agent` already
refuses, so this is that item's to settle - lock, or rely on the branch
refusal and say so.

**Why it matters.** The failure is ordered the wrong way round: the controller
switches first and the refusal arrives afterwards from `assemble_chart_frame`,
so `_halt_every_run` then fails *both* runs over an input to one of them.
`CLAUDE.md`'s expert-review standard asks for interfaces that prevent an error
rather than report it after the fact, and a selector that accepts a choice the
next layer cannot honour is the case that rule names. The port already made the
consequence legible - `present_halt` writes each run's status word and banner
with no frame - which is the right handling of a halt and not a substitute for
not halting.

**Triaged 2026-09-15 as blocked on `PL-8PSW`** rather than ready, per its own
brief: no shipped entry point constructs a two-trunk dashboard, so the defect is
unreachable today, and `PL-8PSW` (overlay two branches) is where two runs first
reach a reader. A branch's `set_agent` already refuses, so whether this needs a
selector lock at all is decided by the shape `PL-8PSW` lands - lock the
selectors while two runs are shown, or rely on the branch refusal and say so
there. Working it before then would design against an interface that does not
exist yet.
