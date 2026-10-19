---
id: PL-J69Y
title: The delegated-worker path closed 3 items since 2026-09-21 and its premise, a cheaper model working delegable items, was ruled out on 2026-10-19 (PL-2D28): decide whether to retire docs/worker.md, docket delegable and not-delegable while keeping verify --self
priority: P2
effort: S
status: needs-decision
classes: planning, docs
feature: defect-review-2026-10
touches: docs/worker.md, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze; a workflow decision that v0.6.0's layout scope does not reach
added: 2026-10-19
---

**Problem.** The delegated-worker path closed 3 items since 2026-09-21 and its premise, a cheaper model working delegable items, was ruled out on 2026-10-19 (PL-2D28): decide whether to retire docs/worker.md, docket delegable and not-delegable while keeping verify --self

**How it was measured.** A defect review on 2026-10-19 read `docs/items` with `docket.store.read_items` and placed each item with `Item.lane(workflow_paths)`. A defect is an item whose `classes` include `defect` or `safety`. An organic defect is one filed before any head's `root-cause-of:` named it and carrying no `reenters:`. The scripts lived in the session's scratchpad and are gone, so this paragraph is the method.

**Why it matters.** The path is either the API runner's contract or 382 lines of upkeep, depending on the answer below.

**Evidence.** Items whose body carries a worker's `**Worked.**` note closed 13, 21, 8, 3 and 37 a week from 2026-08-24 to 09-21, then 0, 0 and 3. `subprojects/docket/README.md` describes `docket delegable` as "what a cheaper model may work". On 2026-10-19 the owner refused a cheaper model or a lower effort for any subagent (`PL-2D28`). What the path still costs:
- `docs/worker.md`, 382 lines
- the `delegable` command
- the `not-delegable:` field on 144 items
- the delegated-review half of `subprojects/docket/src/docket/verify.py`, a 4,092-line module whose items closed 16 in the week of 10-12

**Decided** [superseded 2026-10-19: reopened below, on a cost the case did not carry] (project owner, 2026-10-19, ratified, over keeping the path): retire `docs/worker.md`, `docket delegable`, the `not-delegable:` field and the delegated-review-only code in `verify.py`. Keep `verify --self`, which `git log` names 228 times since 2026-10-01. Parallel work already runs through the Projects coordinator.

**Reopened 2026-10-19, before any of it was built.** The case above missed one consumer. `tools/headless_worker.py`, the API runner (`PL-80R5`, merged as #1666 at 12:08 CDT the same day), runs each item it takes by following `docs/worker.md`. It chooses those items with `bin/docket delegable --ids`. Retiring the path as decided would break the runner. The case's premise does not hold for the runner either. It runs `claude-opus-5-5` (`WORKER_MODEL`), not a cheaper model, and its effort follows the item's lane: `max` for simulator work and `high` for the apparatus. It is paid for by the monthly API credit, which expires unused at the end of each billing cycle. Its work therefore costs no subscription usage, and nothing `PL-2D28` refused applies to it.

**Decision needed.** Keep the delegated-worker path for the API runner, or retire both together? **Recommendation:** keep the path, and narrow this item to rewording. Change `subprojects/docket/README.md`'s "what a cheaper model may work" to "what a headless run may work", and make `docs/worker.md` name the runner as its reader. The runner is the one place where parallel work costs no subscription usage. The three items the path closed since 2026-09-21 predate the runner, so they do not measure it. The question is yours because it reverses a decision you ratified.

**Done when** [superseded 2026-10-19 while the question above is open].

**Done when.** The path and its docs, checks and tests are gone, `verify --self` passes its tests unchanged, and no doc still points at the worker flow.

**Generator check.** Not a head and not a re-entry: a single decision that missed one consumer, `tools/headless_worker.py`, which landed the same day.
