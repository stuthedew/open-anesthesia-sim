---
id: PL-8V6L
title: The agent accounting View prints its residuals in programmer's e-notation, such as '<1e-13 L', which the clinicians who read the screen are not expected to read
priority: P3
effort: S
status: ready
classes: ux
feature: interface-design-review
touches: src/anesthesia_sim/app/formatting.py, tools/glyph_check.py, docs/INTERFACE.md, tests
added: 2026-11-22
payoff: the accounting residuals read as powers of ten in a clinician's notation, not a programming language's
---

**Problem.** The agent accounting View prints its residuals in programmer's e-notation, such as '\<1e-13 L', which the clinicians who read the screen are not expected to read

**Go-ahead.** The design review that found this was approved by the project owner (project owner, 2026-11-22). It ran offscreen on `a7eb53f`, with screenshots of each Workspace and each View at 1366 by 768 and 1920 by 1080 in `/mnt/project-files/v0.7.0/design-review/`.

**What a learner sees.** "Unaccounted: <1e-13 L" and "Absolute error: <1e-13
L" (`view-agent_accounting-1920x1080.png`). `PL-3PJZ` chose to print each
residual as the power of ten it lies below.

**Why it matters.** `.claude/rules/plain-writing.md` lists e-notation such as
"4e-4" among what a clinician reader is not expected to know. The value is
right, but its form is a programming language's.

**What to do.** Keep `PL-3PJZ`'s choice of the bounding power of ten, and
print it as a clinician writes one: "<10⁻¹³ L", with a superscript exponent.
This is a change to how a displayed value is formatted, so it goes through
`app/formatting.py` and its tests. `PL-XFWG` asks whether the two lines should
be one, so work them together.

**Done when.** No accounting line contains "e-", and a formatting test pins
the superscript form.

**Built (2026-11-22).** `format_agent_residual` in `app/formatting.py` keeps
`PL-3PJZ`'s bounding power of ten and writes its exponent in superscript
digits: `<10⁻¹³ L`, and `<10¹ L` for a positive exponent, which has no sign.
The eleven superscript characters were rendered offscreen in the container's
Inter, at device pixel ratios 1 and 2, for every exponent from -20 to 1, and
are recorded in `tools/glyph_check.py`'s `CONFIRMED`. The approved wording
test masks a superscript digit as `^`, as it masks a digit as `#`, so a
residual that moves by a decade does not fail it. `PL-XFWG` (whether the two
residual lines should be one) stays open. It is a change to what a learner
sees, and nothing here depends on its answer. The halted-run notice for a
failed check still prints e-notation from `core/`, filed as `PL-TWZY`.

**Regression run on the code before the fix.**
`test_format_agent_residual_prints_the_power_of_ten_it_lies_below`, run on
`f5c8227` with this branch's test file, fails with
`AssertionError: assert '<1e-12 L' == '<10⁻¹² L'`.

**Docs sweep.** `docs/INTERFACE.md` § "Displayed precision" now shows the
superscript form. `docs/MODEL.md` and `README.md` quote no residual line.
Checked by searching each for "<1e" and "e-13 L".

**Generator check.** A one-off: `PL-3PJZ` chose the bound and wrote it in
Python's own notation.
