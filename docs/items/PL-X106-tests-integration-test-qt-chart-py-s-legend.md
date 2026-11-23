---
id: PL-X106
title: tests/integration/test_qt_chart.py's legend test takes its expected words from trace_legend_label and compared_trace_legend_label, the functions under test, so a wrong legend word passes it
status: untriaged
feature: tests-detect-wrong-values
added: 2026-11-23
filed-pr: 2281
---

**Problem.** tests/integration/test_qt_chart.py's legend test takes its expected words from trace_legend_label and compared_trace_legend_label, the functions under test, so a wrong legend word passes it

**What happens.** `tests/integration/test_qt_chart.py::test_two_runs_on_one_axis_are_told_apart_by_line_width_and_named_in_text` builds the legend words it expects by calling `trace_legend_label` and `compared_trace_legend_label` in `app/dashboard_frame.py`, the functions that write the legend under test. A fault in either function changes the expected words and the drawn words together, so the test passes. `.claude/rules/test-oracles.md` rule 1 asks for an expected value taken from a source independent of the code under test. Found on 2026-11-23 while sorting `PL-00Y5`'s survivors of `app/dashboard_frame.py`.

**What to do.** Take the expected words from the line-style table in `docs/INTERFACE.md`, as `tests/unit/test_dashboard_frame.py::test_each_legend_entry_names_its_compartment_and_line_style_and_then_its_run` now does (`PL-00Y5`), and keep the check that the two runs are drawn with different line widths.
