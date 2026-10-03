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

**Triage 2026-10-03: wider than the title, and classed safety.** Re-measured
on `origin/main` at `9ea31db2`, after `PL-8H2R`, by a probe stepping a
controller to 86 400.0 s at 0.1 s. Any run standing there that no refused step
has stopped reads as an ordinary paused one, and the trunk is one of them:

| Run standing on 86 400.0 s | Limit reason | Status word | Start offered |
| --- | --- | --- | --- |
| trunk halted on a time mark at 24:00:00 | unset | `Paused` | yes |
| branch forked at that halt | unset | `Paused` | yes |
| trunk after its refused step | set | `Stopped — supported run length reached` | no |
| branch at the keyframe a dial laid at 24 h | unset | `Paused` | yes |
| that branch after one refused tick | set | `Stopped — supported run length reached` | no |
| that branch after a reset | unset | `Paused` | yes |

No row with the reason unset shows the limit notice. The marks panel follows
the same latch: an unreached MAC target (fat, 3 ×MAC) stands `still_running`
on the first two rows and `not_reached_within_cap` on the third, which is
`PL-N3N5`'s hazard - a mark read as still ahead of a run that cannot step -
back through the limit's latch rather than the failure's. One more route, read
from the code and not measured: Pause pressed on a tick whose last step lands
on 24:00:00 leaves the trunk paused there with the latch unset.

**Classes `defect, safety`, so `P1` by the safety pin.** Nothing is
miscalculated, as with `PL-N3N5`, which carries the same classes; what is wrong
is the run's state as presented. `docs/MODEL.md` § "Supported run length" says
"What the interface must equally not do is present the stop as a pause", and
`CLAUDE.md`'s clinical-output standard asks that simulation state cannot be
easily misread. A `safety` item runs on the strongest model under the
project's rules, so the triaging session stopped here and yielded its claim.

**What any fix has to reach, read from the code.** Four readers take the
latch: `snapshot()`, `start()`, `_bookmark_standings()` (as `stopped_at_cap`)
and `has_reached_supported_limit`. The second candidate applied to the
snapshot alone would leave `start()` accepting a run whose Start the transport
refuses, and the marks panel as it is. The latch cannot simply go:
`halt_at_supported_limit` records the reason it is handed for a domain limit
raised on any path, which
`test_a_domain_limit_in_a_setting_reaches_the_supported_limit_channel_through_apply_setting`
and `test_the_first_supported_limit_reason_is_the_one_kept` pin. And a reason
derived from the state would also stand on a run still running, on a tick
whose last step lands on 24:00:00, and say `Stopped` beside a live Pause until
the next tick's refused step; halting on arrival in `advance()`, as `_halt_on`
does on a crossing, would close that (inferred, not measured).

**Test cost, measured.** Stepping a controller to 86 400.0 s at 0.1 s took
26.3 s with no mark set and 35.1 s with one, in this container.

**Done when.** Every run standing on the supported run length reads as stopped
there before any step is refused, whichever route put it there: a branch
forked on 86 400.0 s at a keyframe or at a halt, such a branch after a reset,
and a trunk halted on a mark at 24:00:00. For each,
`snapshot().supported_limit_reason` carries the reason the refused step would
give, `start()` raises `SimulationDomainLimitError`, `transport` gives
`start_enabled` false, `notice` gives the limit notice, and an unreached mark
stands `NOT_REACHED_WITHIN_CAP`. Regression tests at 0.1 s cover each route.
