---
id: PL-140X
title: show says 'no item matching' for an id that next and flight name as a live claim, without pointing at stranded or the branch that holds it
status: untriaged
feature: one-snapshot
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-25
---

**Problem.** show says 'no item matching' for an id that next and flight name as a live claim, without pointing at stranded or the branch that holds it

Reproduced live with PL-DRRG: `next` `Excluded, already in flight: PL-DRRG (live claim)`; `show PL-DRRG` `no item matching 'PL-DRRG'`.

**Why it matters.** A dead end at the moment a session asks about work another session holds.

**Done when.** `show` on an id held only on a branch names the branch and how to read it.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn` (PL-P0FP).
