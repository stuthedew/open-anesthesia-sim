---
id: PL-8V6L
title: The agent accounting View prints its residuals in programmer's e-notation, such as '<1e-13 L', which the clinicians who read the screen are not expected to read
status: untriaged
feature: interface-design-review
added: 2026-11-22
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
