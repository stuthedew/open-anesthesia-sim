---
id: PL-7694
title: The compared-run count and a run's index are bare ints checked by hand in seven app functions - run_count at least one in run_trace_style, _hover_context, format_compared_trace_hover, _wash_in_pen and both set_run_count, run_index against it in two and nonnegative in run_label - while off_scale_notice reads frame.runs[run_index] with no check, so an index of -1 answers for the last run under its name (found sweeping PL-ZGYX)
status: untriaged
feature: parse-dont-validate
touches: src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_chart_frame.py, tests/unit/test_dashboard_frame.py, tests/integration/test_qt_chart.py
added: 2026-10-11
---

**Problem.** The compared-run count and a run's index are bare ints checked by hand in seven app functions - run_count at least one in run_trace_style, _hover_context, format_compared_trace_hover, _wash_in_pen and both set_run_count, run_index against it in two and nonnegative in run_label - while off_scale_notice reads frame.runs[run_index] with no check, so an index of -1 answers for the last run under its name (found sweeping PL-ZGYX)

**Found 2026-10-11** by `PL-ZGYX`'s sweep, read from the code on `main` at
`d9340516` and not executed: `off_scale_notice` in `app/dashboard_frame.py`
opens with `run = frame.runs[run_index]` and no check, and Python's negative
indexing makes `-1` the last run. Nothing in `src/` hands it a negative index
today; the count and the index are each a quantity with a domain of its own
(a whole number of runs, at least one; a position among them) checked again at
each way in, which is the shape `.claude/rules/core-domain.md` § "A quantity
with a check of its own is a type, checked once" refuses. A wrong index is the
correct number under another run's name, which `CLAUDE.md`'s standard counts
as a presentation failure.
