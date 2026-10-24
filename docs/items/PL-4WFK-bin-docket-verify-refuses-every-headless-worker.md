---
id: PL-4WFK
title: bin/docket verify refuses every headless worker branch: it counts the run record that the runner commits to docs/worker-runs/ (PL-87BR) as a path outside the item's touches, so PL-K88Z's correct diff came back REJECT on that line alone
priority: P2
effort: S
status: done
classes: defect
feature: worker-instructions
milestone: v0.6.1
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/config.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_portability.py, subprojects/docket/README.md, docket.toml, tools/worker_runs.py
added: 2026-10-24
closed: 2026-10-24
pr: 1715
payoff: a reviewer running bin/docket verify on a headless worker's branch sees the run record named as sanctioned, so a REJECT means real out-of-scope work again
verify: grep -q 'def test_a_worker_run_record_the_branch_added_is_not_outside_touches' subprojects/docket/tests/test_verify.py
---

**Problem.** bin/docket verify refuses every headless worker branch: it counts the run record that the runner commits to docs/worker-runs/ (PL-87BR) as a path outside the item's touches, so PL-K88Z's correct diff came back REJECT on that line alone

**Found** reviewing `PL-K88Z`'s worker branch on 2026-10-24. `bin/docket verify PL-K88Z` printed `FAIL diff stayed inside touches` and named `docs/worker-runs/pl-k88z-worker-20261020T042627.json`. The worker's run record was the only path the worker itself put outside `touches`. `docs/maintainer.md` § on headless workers requires a pushed run to commit that record to its branch, and `tools/worker_runs.py check` fails `make check` until a reviewer writes its review. So every worker branch now carries a file that verify refuses. This was the first record ever committed, which is why nothing caught it sooner. The likely fix is for verify to sanction the record it expects: one file under `docs/worker-runs/` whose name matches the branch. That is the same way it already treats capture and `pr:` edits.

**Reproduced 2026-10-24.** On `claude/pl-k88z-worker`, `bin/docket verify PL-K88Z` printed `FAIL diff stayed inside touches` and listed `docs/worker-runs/pl-k88z-worker-20261020T042627.json` as a path outside `touches`.

**Why it matters.** `docs/maintainer.md` makes verify the first step of reviewing a headless worker's branch. A REJECT on every branch teaches the reviewer to skim past the line, which is where a real out-of-scope edit would also appear.

**Done when.** verify treats a run record as a sanctioned edit and names it as one. A run record here is a `.json` file directly under the run-record folder that the branch added and the base does not hold, and whose `item` field names the item being verified. The folder is spelled once, in `docket.toml`, and `tools/worker_runs.py` reads it from there. A record for another item, a nested file, a file the base already holds, or an uncommitted record is still outside `touches`.

**Generator check.** Not a new head. It is the fifth time verify refused a write that the workflow itself asks for: a capture (`PL-66PR`), a `pr:` record (`PL-ZYQC`), a recurrence (`PL-X5JR`), a recovered body (`PL-3PH2`), and now a worker's run record. Each came from a different writer arriving later, and each was fixed by naming that writer's write as a sanctioned kind. Nothing found here produces such writes faster than the workflow adds writers, so this is fixed as one more kind, not as a mechanism.
