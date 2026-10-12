---
id: PL-7694
title: The compared-run count and a run's index are bare ints checked by hand in seven app functions - run_count at least one in run_trace_style, _hover_context, format_compared_trace_hover, _wash_in_pen and both set_run_count, run_index against it in two and nonnegative in run_label - while off_scale_notice reads frame.runs[run_index] with no check, so an index of -1 answers for the last run under its name (found sweeping PL-ZGYX)
priority: P3
effort: M
status: ready
classes: refactor, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_chart_frame.py, tests/unit/test_dashboard_frame.py, tests/integration/test_qt_chart.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-11
payoff: a run's values can no longer be drawn under another run's name through an unchecked index, and the next chart reader inherits one checked type rather than copying a hand check
verify: grep -q 'def test_off_scale_notice_refuses_a_negative_run_index' tests/unit/test_dashboard_frame.py
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

**Why it matters.** A run's index picks which run's values are drawn under
which run's name, so a wrong one is a correct number under another run's label,
a presentation failure under `CLAUDE.md`'s standard. Seven hand checks guard the
ways in and the eighth reader has none, and the next reader written will copy
whichever it sits beside. Latent: nothing in `src/` passes a negative index.

**Done when.** The count and the index are each checked once, by a type only
that check produces (`.claude/rules/core-domain.md` § "A quantity with a check
of its own is a type, checked once"), the seven functions take the types, and
`off_scale_notice` refuses an index of -1, pinned by
`test_off_scale_notice_refuses_a_negative_run_index` in
`tests/unit/test_dashboard_frame.py`.
