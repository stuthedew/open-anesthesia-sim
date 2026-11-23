---
id: PL-X106
title: tests/integration/test_qt_chart.py's legend test takes its expected words from trace_legend_label and compared_trace_legend_label, the functions under test, so a wrong legend word passes it
priority: P2
effort: S
status: done
classes: test
feature: tests-detect-wrong-values
touches: tests/integration/test_qt_chart.py, src/anesthesia_sim/app/qt_chart.py
added: 2026-11-23
closed: 2026-11-23
pr: 2292
filed-pr: 2281
payoff: a legend that names a trace's compartment, line style or run wrongly fails the drawn-legend test, instead of passing because the test took its expected words from the code that wrote them
tests: tests/integration/test_qt_chart.py::test_two_runs_on_one_axis_are_told_apart_by_line_width_and_named_in_text
---

**Problem.** tests/integration/test_qt_chart.py's legend test takes its expected words from trace_legend_label and compared_trace_legend_label, the functions under test, so a wrong legend word passes it

**What happens.** `tests/integration/test_qt_chart.py::test_two_runs_on_one_axis_are_told_apart_by_line_width_and_named_in_text` builds the legend words it expects by calling `trace_legend_label` and `compared_trace_legend_label` in `app/dashboard_frame.py`, the functions that write the legend under test. A fault in either function changes the expected words and the drawn words together, so the test passes. `.claude/rules/test-oracles.md` rule 1 asks for an expected value taken from a source independent of the code under test. Found on 2026-11-23 while sorting `PL-00Y5`'s survivors of `app/dashboard_frame.py`.

**Why it matters.** The legend is the text that tells a learner which line belongs to which compartment and which run, and `docs/INTERFACE.md` § "The six compartment traces: what separates them" says a trace mistaken for another gives a wrong clinical value. This is the one test that reads the legend drawn beside a real two-run chart, so its expected words should not depend on the functions that wrote them. The unit test added in `PL-00Y5` now pins the words those functions return, but nothing pins the drawn words if the legend is later built some other way. The test also takes the run names from `run_label` and the wash-in legend's words from `WASH_IN_TRACE_LEGEND_LABEL`, which are code under test too.

**What to do.** Take the expected words from the line-style table in `docs/INTERFACE.md`, as `tests/unit/test_dashboard_frame.py::test_each_legend_entry_names_its_compartment_and_line_style_and_then_its_run` now does (`PL-00Y5`), and keep the check that the two runs are drawn with different line widths.

**Done when.** The legend test in `tests/integration/test_qt_chart.py` expects, for both the concentration chart and the wash-in chart, legend words written as literals: each compartment's name and line style from the table in `docs/INTERFACE.md` § "The six compartment traces: what separates them", and each run's name as "Run" followed by its number, from § "Naming the run in a comparison". The test fails when `trace_legend_label`, `compared_trace_legend_label` or `run_label` returns other words.

**Generator check.** A leftover instance of the fact that `PL-CMJ5` states, where a test's expected value comes from. The test was written on 2026-09-15 in #618, a month before `.claude/rules/test-oracles.md` (2026-10-17), and that rule applies to a test when it is written or changed, so this is not a re-entry: the rule never reached it.

**Done 2026-11-23.** The legend test now writes its expected words out: each compartment's name and line style from the table in `docs/INTERFACE.md`, "Run" followed by the run's number, the wash-in legend's "F<sub>A</sub>/F<sub>I</sub> (solid)" and the branch point's "Branch point (vertical, solid)". The last two are the words in `tests/integration/approved_interface_strings.json`, since `docs/INTERFACE.md` describes those lines without quoting their legend entries. Five errors planted by hand, one at a time, each failed the new test and passed the old one: the line style replaced by the compartment's name, the run and compartment swapped in an entry, every run numbered one higher, the wash-in line called dashed, and the branch point's entry given a control change's words. The blind review found two more ways the test could pass a wrong legend. `TraceLegend.branch_mark` in `app/qt_chart.py` returned the branch point's words from the constant rather than from the drawn label, so a branch entry drawn with a control change's words passed. The wash-in legend's entries were checked as a set of words, never each against its own curve's pen, so run names given to the other run's curve passed. Both legends now read every entry back from the label and swatch they draw, through one helper, and the test reads the wash-in legend's branch entry and pairs each wash-in entry with its curve's pen. Each of the review's three errors, planted by hand, failed the fixed test and passed the previous commit's.

Docs checked for statements this change made untrue: `docs/INTERFACE.md` § "The six compartment traces: what separates them" and § "Naming the run in a comparison", `docs/ARCHITECTURE.md` and `README.md` (neither names the legend's readback), and the items that cite the test (`PL-8PSW`, `PL-VM1Q`), which are closed records.
