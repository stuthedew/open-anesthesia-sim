---
id: PL-4WFK
title: bin/docket verify refuses every headless worker branch: it counts the run record that the runner commits to docs/worker-runs/ (PL-87BR) as a path outside the item's touches, so PL-K88Z's correct diff came back REJECT on that line alone
status: untriaged
touches: subprojects/docket/src/docket/verify.py
added: 2026-10-24
---

**Problem.** bin/docket verify refuses every headless worker branch: it counts the run record that the runner commits to docs/worker-runs/ (PL-87BR) as a path outside the item's touches, so PL-K88Z's correct diff came back REJECT on that line alone

**Found** reviewing `PL-K88Z`'s worker branch on 2026-10-24. `bin/docket verify PL-K88Z` printed `FAIL diff stayed inside touches` and named `docs/worker-runs/pl-k88z-worker-20261020T042627.json`. The worker's run record was the only path the worker itself put outside `touches`. `docs/maintainer.md` § on headless workers requires a pushed run to commit that record to its branch, and `tools/worker_runs.py check` fails `make check` until a reviewer writes its review. So every worker branch now carries a file that verify refuses. This was the first record ever committed, which is why nothing caught it sooner. The likely fix is for verify to sanction the record it expects: one file under `docs/worker-runs/` whose name matches the branch. That is the same way it already treats capture and `pr:` edits.
