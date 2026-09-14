---
id: PL-B5DW
title: docket status's plan header calls the anchor 'the step the project is on' while wave reports the step as a different row
status: untriaged
added: 2026-09-14
---

**Problem.** docket status's plan header calls the anchor 'the step the project is on' while wave reports the step as a different row

**Found 2026-09-14 while closing `PL-FWJF`.** `format_status`'s plan header
(`render._plan_header`) prints `Plan: v0.4.26 — the interface moves to Qt, the
step the project is on.` while `bin/docket wave` on the same tree prints `Step
between numbered steps (— on the timeline): v0.4.x — the code is the model`.
Before `PL-FWJF` it said the same of v0.5.0. `docket next` already
distinguishes the two - `PL-1J0P` gave it "In scope for {anchor}, which the
step the project is on ({step_label}) comes before" - and `Scope.step_label`
carries the row, so the header has what it needs and does not read it.

**Why it is an item and not a fix-now.** The header is a one-line budget beside
the legend, and the `next` sentence is too long for it; choosing the wording,
and pinning the new branch with a test, is a decision rather than a typo.

**Done when** the header names the step apart from the anchor whenever
`Scope.step_label` is set, and a test in `test_release.py` or `test_roadmap.py`
pins it against a plan standing on a patch-track row.
