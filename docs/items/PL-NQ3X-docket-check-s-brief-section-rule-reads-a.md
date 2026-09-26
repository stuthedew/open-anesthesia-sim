---
id: PL-NQ3X
title: docket check's brief-section rule reads a fenced copy of the capture template above the real sections and reports 'brief has nothing under Why it matters', under --verify too
priority: P3
effort: S
status: done
classes: defect
feature: exact-gates
milestone: v0.5.12
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-25 triage pass
added: 2026-09-25
closed: 2026-09-26
pr: 1089
payoff: a brief can quote the capture template in a fenced example without docket check refusing the real sections beneath it
verify: grep -q 'def test_a_fenced_copy_of_the_capture_template_is_not_the_brief' subprojects/docket/tests/test_checks.py
---

**Problem.** docket check's brief-section rule reads a fenced copy of the capture template above the real sections and reports 'brief has nothing under Why it matters', under --verify too

Reproduced: a brief quoting the template in a fence, then carrying real sections, fails. Close to PL-6G8T.

Re-confirmed 2026-09-25 against 46954a81: a scratch store holding one `ready` item whose problem paragraph quotes the three template headings in a fence, followed by real why-it-matters and done-when sections, fails `bin/docket check` with `brief has nothing under **Why it matters.**` (1 error, exit 1), so `docket set` would refuse it too. `_section_text` judges the first line-initial marker, deliberately, so that a stub above a real brief still fails; a fence is the one place a line-initial marker is certainly a quotation, and blanking it leaves the stub case alone.

`PL-6G8T` (open, `P2`, `ready`) is the same function's false pass: a required heading quoted at a line break is taken as the section and masks an empty real one. One change to how `_section_text` finds a heading can answer both, so work them together.

**Generator check.** The fact misread is whether a line opening with a required heading's words is the brief's heading or a quotation of one, recognised by the words at line start - `PL-GPJ7`'s `misread:`, and a member of it correctly. `PL-6G8T` misreads the same fact from the passing side and is not in `PL-GPJ7`'s `root-cause-of:`.

**Why it matters.** A false refusal on a correct brief.

**Done when.** Fenced blocks are blanked before the section scan; a test holds the reproduction.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Closed 2026-09-26, in `PL-GPJ7`'s step 3.** `_section_text` and `_stub_above_brief` find headings through `_without_fences`, which blanks every closed fenced block by CommonMark's rules. A backtick opener's info string holds no backtick, so the triple-backtick code span wrapped to a line's start in `PL-6SRZ` opens nothing, and a fence left unclosed is read as written rather than hiding every section below it. The text under a heading is still sliced from the brief, so a fence under a heading is text under it. Measured on the store, one reading changed, a closed item's `**Decision needed.**` that stands only inside a fence (`PL-VJ1X`). `test_a_fenced_copy_of_the_capture_template_is_not_the_brief` holds the reproduction.
