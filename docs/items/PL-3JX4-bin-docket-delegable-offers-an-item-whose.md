---
id: PL-3JX4
title: bin/docket delegable offers an item whose touches name a new apparatus test file under tests/ that workflow_paths does not list, and tools/workflow_paths_check.py refuses such a test once it is tracked, so the worker can only block; the path alone cannot say whether the test will import anesthesia_sim, so PL-GKX6 left tests/ out of its placement condition
priority: P3
effort: S
status: dropped
classes: defect
feature: worker-runs
touches: subprojects/docket/src/docket/model.py
added: 2026-10-27
closed: 2026-10-31
reason: no offered item has the shape (0 of 57 on 2026-10-27), the failure is loud because the worker blocks on tools/workflow_paths_check.py's refusal, and the only rule available forecasts an unwritten test's imports from the item's lane, a judgment the apparatus does not script; reopen on the first worker that blocks this way
---

**Problem.** bin/docket delegable offers an item whose touches name a new apparatus test file under tests/ that workflow_paths does not list, and tools/workflow_paths_check.py refuses such a test once it is tracked, so the worker can only block; the path alone cannot say whether the test will import anesthesia_sim, so PL-GKX6 left tests/ out of its placement condition

**Found 2026-10-27, closing `PL-GKX6`.** `workflow_paths` lists each apparatus
test under `tests/unit/` by name. `problems` in `tools/workflow_paths_check.py`
refuses a test file there that imports no `anesthesia_sim` and that the list
does not name. So a delegated item that creates a test for a new `tools/`
script also needs an edit to `docket.toml`, a gate path. `placed_by_neither`
in `docket.model` passes every path under `TESTS`, because a file there is
placed by its imports. Until the file is written, nothing can read those.

**Measured 2026-10-27:** none of the 57 items `bin/docket delegable --ids`
offered names a test file under `tests/` that does not exist and that
`workflow_paths` does not cover. The risk is real, but no offered item has it
today.

**A possible rule.** An item whose other `touches` all fall in the workflow
lane will write an apparatus test, so such an item could be withheld when it
names a missing, unlisted test file under `tests/`. That reads the item's lane
as a forecast of the test's imports, which is a judgment, so it is worth
building only if such items start being offered.

**Why it matters.** A worker given such an item can only block, because the test it must write is refused until `docket.toml`, a gate path, places it. That costs one delegated run and a session's attention.

**Done when.** `bin/docket delegable` withholds an item whose `touches` name a missing test file under `tests/` that `workflow_paths` does not list, where its other paths all lie in the workflow lane.

**Generator check.** A one-off. The fact is whether a test file not yet written is apparatus or product. No reader can know it before the file exists, and no head states it.

**Dropped at triage, 2026-10-31.** None of the 57 items `bin/docket delegable` offered on 2026-10-27 has this shape, so nothing is downstream of leaving it. The failure is loud: the worker blocks, and `tools/workflow_paths_check.py` says why. The only available rule treats an item's lane as a forecast of the imports of a test that does not exist yet. That is a judgment, and `CLAUDE.md` refuses to script judgment into a tool. Reopen this item the first time a worker blocks on such a test.
