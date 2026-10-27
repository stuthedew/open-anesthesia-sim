---
id: PL-3JX4
title: bin/docket delegable offers an item whose touches name a new apparatus test file under tests/ that workflow_paths does not list, and tools/workflow_paths_check.py refuses such a test once it is tracked, so the worker can only block; the path alone cannot say whether the test will import anesthesia_sim, so PL-GKX6 left tests/ out of its placement condition
status: untriaged
feature: worker-runs
added: 2026-10-27
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
