---
id: PL-TY1Z
title: docket's checks.SUPERSEDED needs a literal space after its keyword, so a [superseded marker a soft break wraps before its date is not recognised and the passage it retires is read as standing; latent
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests
added: 2026-10-04
---

**Problem.** docket's checks.SUPERSEDED needs a literal space after its keyword, so a [superseded marker a soft break wraps before its date is not recognised and the passage it retires is read as standing; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

CommonMark § 6.7. `SUPERSEDED` needs a literal space after "superseded", so `_left_statuses` on a ready item whose brief reads "[superseded" wrapped onto "2026-09-30: answered] Left at `needs-decision` until the owner answers." reports the status mismatch the one-line marker suppresses, and `_answered_beneath` reads an answer a wrapped marker withdrew. `statement_lines` reads the passage as one statement; only the marker pattern misses. Read by `_standing`, and through it `_left_statuses`, `_undeclared_prerequisites`, `_ended_waits` and `_answered_beneath`. Latent: the 87 markers in 65 tracked files each sit on one line.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
