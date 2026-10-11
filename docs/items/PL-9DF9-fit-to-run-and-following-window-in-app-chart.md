---
id: PL-9DF9
title: fit_to_run and following_window in app/chart_time_base.py each check by hand that newest_sample_s is finite and nonnegative on a bare float, where the one caller hands them the newest run snapshot's elapsed_s, a case instant: the chart time base is a holder of a case instant PL-CN5S left untyped, beside PL-RCYZ's control record (found sweeping PL-ZGYX)
status: untriaged
feature: parse-dont-validate
touches: src/anesthesia_sim/app/chart_time_base.py, src/anesthesia_sim/app/chart_frame.py, tests/unit/test_chart_time_base.py
added: 2026-10-11
---

**Problem.** fit_to_run and following_window in app/chart_time_base.py each check by hand that newest_sample_s is finite and nonnegative on a bare float, where the one caller hands them the newest run snapshot's elapsed_s, a case instant: the chart time base is a holder of a case instant PL-CN5S left untyped, beside PL-RCYZ's control record (found sweeping PL-ZGYX)

**Found 2026-10-11** by `PL-ZGYX`'s sweep, on `main` at `d9340516`: both
functions open with the same `newest sample time must be finite and
non-negative` refusal, and `assemble_chart_frame` in `app/chart_frame.py`
computes the value as `max(run.snapshot.elapsed_s for run in runs)`. Typing the
parameter `CaseInstant` and requiring it where it enters
(`require_case_instant`) removes both hand checks; whether the snapshot's
`elapsed_s` is already typed `CaseInstant` is the first thing to confirm.
