---
id: PL-5291
title: A branch built standing on the 24 h supported run length still offers Start, because SimulationController._open_at never sets _supported_limit_reason, the only limit signal the transport's stopped state reads, against Transport's own docstring
status: untriaged
feature: numerical-domain
added: 2026-10-03
---

**Problem.** A branch built standing on the 24 h supported run length still offers Start, because SimulationController._open_at never sets _supported_limit_reason, the only limit signal the transport's stopped state reads, against Transport's own docstring

**Measured 2026-10-03** by the first review of #1292 (`PL-73ZN`, `PL-BMY5`),
and reproduced the same day at the shipped 0.1 s step. A trunk halted at
24:00:00 offers no Start: `halt_at_supported_limit` set
`_supported_limit_reason`, and `dashboard_frame.transport` treats the run as
stopped when that or `failure_reason` is set (`dashboard_frame.py:1125`). A
branch forked from it on 86 400.0 s - at the keyframe a dial moved at the
halt lays there, or at a bookmark on 24:00:00 - is a new controller standing at
step count 864 000, which `SimulationState` accepts, since a run may stand on
the limit. Nothing sets its latch: `_open_at` (`controller.py`) builds the
state and the definition and never asks whether the state has room for a
step, and only a refused step calls `halt_at_supported_limit`. So the branch
offers Start, and the limit notices that read the same field
(`dashboard_frame.py:688`, `:1183`) say nothing. Pressing Start takes one
refused tick, after which Start goes and the notice appears. A branch reset
goes back to the fork, clears the latch (`controller.py:1506`) and offers
Start again. The review's probe printed, in order: trunk `start_enabled
False`; branch at 86400.0, count 864000, limit flag False, `start_enabled
True`; after the first tick `start_enabled False`; after a branch reset
`start_enabled True`.

**Why it matters.** `Transport`'s docstring makes Start false for a run that
"stands at the supported run length", and `halt_at_supported_limit` says why:
"a Start that does nothing is a control presenting itself as working". Until
the learner presses it, a branch with no span left reads as an ordinary paused
run, which is the hidden-mode and stale-state hazard `.claude/rules/expert-review.md`
names. Nothing is miscalculated; every value shown is a completed step's. It is
older than #1292, which made a state at the limit an explicitly legal one to
build and tested the build but not what it shows.

**Candidate fix.** Derive "stands at the supported run length" from the run
rather than from a latch only a refused step sets: either `_open_at` and the
branch reset set the latch when `require_supported_run_length` would refuse
the state's first step, or the snapshot reports it from `step_count >=
maximum_step_count(simulation_step_s)` directly. The second leaves no second
mode to keep in step with the first. Regression tests at 0.1 s: a fork on
86 400.0 and a branch reset there each give `start_enabled` false and the
limit notice.
