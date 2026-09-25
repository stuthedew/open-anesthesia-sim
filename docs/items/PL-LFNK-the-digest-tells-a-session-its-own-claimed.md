---
id: PL-LFNK
title: The digest tells a session its own claimed capture has 'no copy here to start from' while show says it is in flight on this branch, because Hold.on_base and vcs.stranded answer 'is this item only on a branch' two ways (render.py:512 vs :535)
status: untriaged
feature: one-snapshot
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_cli.py
added: 2026-09-25
---

**Problem.** The digest tells a session its own claimed capture has 'no copy here to start from' while show says it is in flight on this branch, because Hold.on_base and vcs.stranded answer 'is this item only on a branch' two ways (render.py:512 vs :535)

Reproduced in a scratch branch holding its own claimed capture: digest `Filed on a branch, not yet on origin/main: PL-DRRG, PL-ZZZZ - no copy here to start from`; `show PL-ZZZZ` `IN FLIGHT on this branch ... this session's own work`; `stranded` lists only PL-DRRG. Live, the digest named PL-DRRG on two consecutive lines.

**Why it matters.** Two answers to one question at session start.

**Done when.** One predicate for 'only on a branch'; the digest names the session's own branch as here.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
