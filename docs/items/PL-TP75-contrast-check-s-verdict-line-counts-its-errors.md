---
id: PL-TP75
title: contrast_check's verdict line counts its errors from a different list than its exit code, so a chart trace below the floor fails the run under a header reading 0 errors
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: tools/contrast_check.py, tests/unit/test_contrast_check.py
added: 2026-09-24
payoff: A reader who stops at the contrast report's first line is never told a failing run has 0 errors
verify: grep -q 'def test_a_run_failing_on_a_trace_alone_says_so_in_its_header' tests/unit/test_contrast_check.py
---

**Problem.** `tools/contrast_check.py` decides whether a run failed in one
place and counts its failures in another, and the two lists have drifted.
`Report.errors` decides the exit code from eight kinds of error, including
`below_trace_floor`; `format_report` sums its own `error_count` for the verdict
line from seven, and `below_trace_floor` is the one it leaves out. So a run
whose only error is a chart trace under `TRACE_FLOOR` in one vision model exits
1, prints the "Chart traces below 3.0:1 against PANEL" section, and heads it
with `... 0 known shortfalls, 0 errors`.

Reproduced 2026-09-24 against a miniature tree holding `MUSCLE_COLOR =
"#D97706"` - the colour `test_a_trace_below_the_floor_in_one_model_alone_is_an_error`
already uses, 2.98:1 for a deuteranope - with `errors` true and the header
reading `0 errors`.

**Why it matters.** The verdict line is the part of the report a reader trusts
most and the part `test_the_shipped_palette_holds` asserts on, and
`.claude/rules/apparatus-standard.md`'s floor is that what a check reports must
be true. The mechanism is the defect rather than the one omission: every error
kind is listed twice, so each new one is a chance to update one list and not
the other. `PL-KNHX` adds a ninth kind in the same change, which is the moment
this would repeat.

**Where.** `tools/contrast_check.py`, `Report.errors` and `format_report`;
`tests/unit/test_contrast_check.py`.

**Done when.** One list decides both the exit code and the count the verdict
line prints, so the two cannot disagree, and a test holds the header of a run
failing on a trace alone to its real count.
