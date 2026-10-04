---
id: PL-TY1Z
title: docket's checks.SUPERSEDED needs a literal space after its keyword, so a [superseded marker a soft break wraps before its date is not recognised and the passage it retires is read as standing; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-04
pr: 1358
payoff: a passage its writer marked superseded is read as retired however the marker wraps, so no check advises on a state the brief has already left
verify: grep -qF '"superseded marker, ' tests/unit/test_doc_check.py
---

**Problem.** docket's checks.SUPERSEDED needs a literal space after its keyword, so a [superseded marker a soft break wraps before its date is not recognised and the passage it retires is read as standing; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

CommonMark § 6.7. `SUPERSEDED` needs a literal space after "superseded", so `_left_statuses` on a ready item whose brief reads "[superseded" wrapped onto "2026-09-30: answered] Left at `needs-decision` until the owner answers." reports the status mismatch the one-line marker suppresses, and `_answered_beneath` reads an answer a wrapped marker withdrew. `statement_lines` reads the passage as one statement; only the marker pattern misses. Read by `_standing`, and through it `_left_statuses`, `_undeclared_prerequisites`, `_ended_waits` and `_answered_beneath`. Latent: the 87 markers in 65 tracked files each sit on one line.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `09cdc761`, `checks._standing` over a passage opening "[superseded" wrapped onto "2026-09-30: answered] Left at `needs-decision` until the owner answers." returns True, where the same marker on one line returns False.

**Why it matters.** The marker is the one way a brief retires a passage without deleting its history, and `_left_statuses`, `_undeclared_prerequisites`, `_ended_waits` and `_answered_beneath` all read through it, so a marker a reflow wraps before its date leaves those checks advising on, or refusing over, a passage its writer has already retired.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** `SUPERSEDED` reads a marker whose keyword and date a soft break separates as the marker it is, and a blank line or a block's start still ends it; a `superseded marker, ...` case in `CONTINUED_STATEMENTS` pins it.
