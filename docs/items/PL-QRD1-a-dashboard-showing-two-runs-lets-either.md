---
id: PL-QRD1
title: A dashboard showing two runs lets either selector switch its own agent, which the shared MAC axis then refuses only after the controller has switched: lock the selectors while two runs are shown, with PL-8PSW
priority: P3
effort: S
status: blocked
classes: defect, ux
feature: scenario-branching
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py
blocked-by: PL-8PSW, PL-XJ37
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

## Groomed 2026-09-20 under `PL-JFQ3`: the premise that `PL-8PSW` would settle it was wrong

**What the brief expected.** That `PL-8PSW` (overlay two branches on one time
axis) "is where two runs first reach a reader", so it would settle whether this
needs a selector lock at all — "lock, or rely on the branch refusal and say
so".

**What `PL-8PSW` actually landed.** The drawing, not the route.
`src/anesthesia_sim/app/main.py` constructs `SimulationView((controller,))`
with one controller and mentions no branch, and `dashboard_frame.transport`
still computes `selector_locked=snapshot.is_running` — locked while *running*,
which is the discards-the-case rule, and not while two runs are shown. So
neither disposition was taken: the selectors are not locked on a two-run
dashboard, and nothing says the branch refusal is being relied on instead.

**The defect is therefore still exactly as unreachable as the triage said**,
and for the reason the triage gave: no shipped entry point constructs a
two-trunk dashboard. What was wrong was only *which item* makes one reachable.

**The real blocker, now declared.** `PL-XJ37` (nothing in v0.5.0's scope lets a
learner take a fork or select between runs, and `SimulationView`'s run set is
fixed at construction), `needs-decision`, written into `blocked-by` beside
`PL-8PSW`. The question the brief poses is unchanged and is `PL-XJ37`'s to
settle for the same reason it was `PL-8PSW`'s: working it before then designs
against an interface that does not exist yet.
