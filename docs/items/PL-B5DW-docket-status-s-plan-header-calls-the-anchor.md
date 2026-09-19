---
id: PL-B5DW
title: docket status's plan header calls the anchor 'the step the project is on' while wave reports the step as a different row
priority: P3
effort: S
status: done
classes: defect, infra
feature: timeline-arrangement
touches: subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_roadmap.py
added: 2026-09-14
closed: 2026-09-19
verify: uv run pytest subprojects/docket/tests/test_roadmap.py && grep -q 'def test_the_plan_header_names_the_step_apart_from_the_anchor' subprojects/docket/tests/test_roadmap.py
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

**Why it matters.** The two commands are read by the same session minutes apart
- `status` at session start, `wave` when deciding what beat is due - and they
disagree about which row the project is standing on while using the same words
for it. A session that believes the anchor *is* the step will scope work to the
wrong milestone, which is the one mistake the planning cadence exists to
prevent; `PL-1J0P` already had to teach `next` the same distinction, so this is
the third command asked the same question and the only one still answering it
from the wrong field.

**Closed 2026-09-19 under `PL-2T03`.** `render._plan_header` names the row
apart from the anchor whenever `Scope.step_label` is set: `Plan: v0.4.26 — the
interface moves to Qt, the milestone due next; the project stands on v0.4.x —
the code is the model.` on the implementing beat, and the same `; the project
stands on ...` clause appended on the clearing beat. Where the two are one row
the header reads as before. Pinned by
`test_the_plan_header_names_the_step_apart_from_the_anchor`.
