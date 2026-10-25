---
id: PL-9DF9
title: fit_to_run and following_window in app/chart_time_base.py each check by hand that newest_sample_s is finite and nonnegative on a bare float, where the one caller hands them the newest run snapshot's elapsed_s, a case instant: the chart time base is a holder of a case instant PL-CN5S left untyped, beside PL-RCYZ's control record (found sweeping PL-ZGYX)
priority: P3
effort: S
status: done
classes: refactor
feature: parse-dont-validate
touches: src/anesthesia_sim/app/chart_time_base.py, src/anesthesia_sim/app/chart_frame.py, tests/unit/test_chart_time_base.py, tests/unit/test_chart_frame.py, tests/unit/test_supported_range_edges.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-11
closed: 2026-10-24
pr: 1766
payoff: the chart's time window takes a checked case instant once, so its two functions cannot drift apart on which instants they admit
verify: ! grep -qF 'newest sample time must be finite' src/anesthesia_sim/app/chart_time_base.py
---

**Problem.** fit_to_run and following_window in app/chart_time_base.py each check by hand that newest_sample_s is finite and nonnegative on a bare float, where the one caller hands them the newest run snapshot's elapsed_s, a case instant: the chart time base is a holder of a case instant PL-CN5S left untyped, beside PL-RCYZ's control record (found sweeping PL-ZGYX)

**Found 2026-10-11** by `PL-ZGYX`'s sweep, on `main` at `d9340516`: both
functions open with the same `newest sample time must be finite and
non-negative` refusal, and `assemble_chart_frame` in `app/chart_frame.py`
computes the value as `max(run.snapshot.elapsed_s for run in runs)`. Typing the
parameter `CaseInstant` and requiring it where it enters
(`require_case_instant`) removes both hand checks; whether the snapshot's
`elapsed_s` is already typed `CaseInstant` is the first thing to confirm.

**Why it matters.** Two hand checks of one quantity on a bare float is the
shape `.claude/rules/core-domain.md` refuses, and the time base decides which
samples the chart draws and where, so the two checks drifting apart would let
one window admit an instant the other refuses. No behaviour changes: the one
caller hands a value the snapshot already checked.

**Done when.** `fit_to_run` and `following_window` take the newest sample as a
`CaseInstant`, checked once where `assemble_chart_frame` reads it, neither
carries the `newest sample time must be finite` refusal, and the tests in
`tests/unit/test_chart_time_base.py` that pinned the refusal move to the parse.

**Closed 2026-10-24.** `fit_to_run` and `following_window` take `newest_instant_s: CaseInstant` and check nothing. `assemble_chart_frame` checks the newest snapshot's `elapsed_s` once with `require_case_instant`, and `test_the_frame_refuses_a_newest_instant_not_built_as_one` in `tests/unit/test_chart_frame.py` pins that. The two refusal tests in `tests/unit/test_chart_time_base.py` became one test that an instant off the case's axis cannot be built as a `CaseInstant`. Two tests there passed instants past the 24 h supported run length (500 000 s, and 3 and 10 times the widest rung), which no run can reach. They now use 86 400 s, and the doubling test checks the one doubling a case can reach, from 12 h to 24 h.
