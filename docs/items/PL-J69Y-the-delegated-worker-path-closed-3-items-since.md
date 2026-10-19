---
id: PL-J69Y
title: The delegated-worker path closed 3 items since 2026-09-21 and its premise, a cheaper model working delegable items, was ruled out on 2026-10-19 (PL-2D28): decide whether to retire docs/worker.md, docket delegable and not-delegable while keeping verify --self
status: untriaged
feature: defect-review-2026-10
added: 2026-10-19
---

**Problem.** The delegated-worker path closed 3 items since 2026-09-21 and its premise, a cheaper model working delegable items, was ruled out on 2026-10-19 (PL-2D28): decide whether to retire docs/worker.md, docket delegable and not-delegable while keeping verify --self

**How it was measured.** A defect review on 2026-10-19 read `docs/items` with `docket.store.read_items` and placed each item with `Item.lane(workflow_paths)`. A defect is an item whose `classes` include `defect` or `safety`. An organic defect is one filed before any head's `root-cause-of:` named it and carrying no `reenters:`. The scripts lived in the session's scratchpad and are gone, so this paragraph is the method.

**Evidence.** Items whose body carries a worker's `**Worked.**` note closed 13, 21, 8, 3 and 37 a week from 2026-08-24 to 09-21, then 0, 0 and 3. `subprojects/docket/README.md` describes `docket delegable` as "what a cheaper model may work". On 2026-10-19 the owner refused a cheaper model or a lower effort for any subagent (`PL-2D28`). What the path still costs:
- `docs/worker.md`, 382 lines
- the `delegable` command
- the `not-delegable:` field on 144 items
- the delegated-review half of `subprojects/docket/src/docket/verify.py`, a 4,092-line module whose items closed 16 in the week of 10-12

**Decided** (project owner, 2026-10-19, ratified, over keeping the path): retire `docs/worker.md`, `docket delegable`, the `not-delegable:` field and the delegated-review-only code in `verify.py`. Keep `verify --self`, which `git log` names 228 times since 2026-10-01. Parallel work already runs through the Projects coordinator.

**Done when.** The path and its docs, checks and tests are gone, `verify --self` passes its tests unchanged, and no doc still points at the worker flow.
