---
id: PL-CBDX
title: Read every simulator diff merged unread since 2026-09-23 against the safety-critical standard, since the review hold was clicked through rather than read
priority: P1
effort: M
status: ready
classes: safety
feature: review-hold
touches: docs/items, src/anesthesia_sim
added: 2026-09-25
payoff: any wrong or misleading clinical value an unread merge put on screen since 2026-09-23 is found and filed, or the record says none was
verify: grep -qF '**Reviewed.**' docs/items/PL-CBDX-*.md
not-delegable: the work is a read of merged diffs against the safety-critical standard; no command can prove a diff was read well, and the brief asks for a clean-context session on the strongest model
---

**Problem.** Read every simulator diff merged unread since 2026-09-23 against the safety-critical standard, since the review hold was clicked through rather than read

The owner's answer of 2026-09-25 under `PL-SQTR` confirmed that pull requests `bin/docket arm` held for review were armed in the browser without being read. So every merged diff since 2026-09-23 that touches `src/`, `tests/` outside `subprojects/`, `docs/MODEL.md`, `src/anesthesia_sim/data/` or `README.md` reached `main` with no read against the safety-critical standard.

**Why it matters.** This is the one path by which an unread merge could have put a wrong or misleading clinical value on screen, and `CLAUDE.md`'s standard assumes a clinician could act on one.

**Done when.** A fresh session, with a clean context and the strongest model, has read each such diff against `CLAUDE.md`'s safety-critical clinical-output standard and filed each finding with `bin/docket new`. It then adds a Reviewed section to this brief: one line per pull request read, with what it found, or that it found nothing.

**Generator check.** A one-off, from `PL-SQTR`'s owner-raised finding: a human step was skipped, and no record was misread.
