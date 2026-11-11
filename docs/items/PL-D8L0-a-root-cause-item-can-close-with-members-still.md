---
id: PL-D8L0
title: A root-cause item can close with members still open and with a 'spent' verdict that names no check: 37 of 90 heads closed the day they were added, 11 of them with members open
priority: P2
effort: M
status: ready
classes: defect
feature: generator-measurement
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests, .claude/skills/docket/modes/triage.md
deferred-from: v0.7.0 - found by the 2026-11-10 audit after the freeze; apparatus, and it changes no displayed value, so the release does not wait on it
added: 2026-11-10
payoff: a root cause closed on a sweep, on silence or before its members are fixed reads differently from one closed by a check
verify: grep -rq 'def test_a_closed_head_whose_members_are_open_is_marked' subprojects/docket/tests
---

**Problem.** A root-cause item can close with members still open and with a 'spent' verdict that names no check: 37 of 90 heads closed the day they were added, 11 of them with members open

**Checked 2026-11-10:** `generator_faults` in `subprojects/docket/src/docket/model.py` asks nothing of a closed item; its docstring says a verdict on a closed item is read by nothing. A script over the store's front matter found 11 heads with no `generator:` field: `PL-2T03`, `PL-4FBP`, `PL-4Q9B`, `PL-6TP8`, `PL-9HD1`, `PL-BHVM`, `PL-G21K`, `PL-G424`, `PL-HWW1`, `PL-L4YG`, `PL-TZ7T`. Three heads are marked spent on a verdict that names no check or type: `PL-GTH6` and `PL-VDWT` ("no member filed since") and `PL-CMJ5` (a prose rule). The audit's reviewer reported that 37 of 90 heads closed on the day they were added, 11 of them with members open; the filing session did not recount that.

**Why it matters.** A head is the record that a root cause was found and stopped. The audit of 2026-11-10 found that the fixes which held each had a check or a checked type, and the ones that did not hold were sweeps or prose. A head that closes on a sweep, on silence, or before its members are fixed reads the same in every report as one closed by a check, and it sets no pause.

**Done when.** A head's verdict at close names the check, type or single writer that stops the next member, or says that none exists and why. `bin/docket generators` marks a closed head whose members are still open, and one whose verdict names no mechanism. Heads already closed are not rewritten.

**Generator check.** A defect in what a head records, which `.claude/skills/docket/modes/triage.md` places under work on the generators. A one-off as a mechanism.
