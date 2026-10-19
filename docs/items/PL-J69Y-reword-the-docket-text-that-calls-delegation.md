---
id: PL-J69Y
title: Reword the docket text that calls delegation handing work to a cheaper model, so it describes the API runner, which runs the same model on the API credit; the worker path and its code stay (project owner, 2026-10-19)
priority: P2
effort: S
status: dropped
classes: docs
feature: defect-review-2026-10
touches: docs/worker.md, subprojects/docket/README.md, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/
deferred-from: v0.6.0 - captured after the freeze; a workflow decision that v0.6.0's layout scope does not reach
added: 2026-10-19
closed: 2026-10-19
reason: deleted at the project owner's ask, 2026-10-19: the worker path stays for the API runner, and the rewording is not wanted
payoff: the docs describe the API runner as what it is, the same model on the API credit, not a cheaper one
verify: ! grep -rq 'cheaper model' subprojects/docket/README.md subprojects/docket/src && grep -q 'API runner' docs/worker.md
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

**Decision needed.** Keep the delegated-worker path for the API runner, or retire both together? [superseded 2026-10-19: answered below] **Recommendation:** keep the path, and narrow this item to rewording. Change `subprojects/docket/README.md`'s "what a cheaper model may work" to "what a headless run may work", and make `docs/worker.md` name the runner as its reader. The runner is the one place where parallel work costs no subscription usage. The three items the path closed since 2026-09-21 predate the runner, so they do not measure it. The question is yours because it reverses a decision you ratified.

**Answer** (project owner, 2026-10-19): "We just implemented this api runner today so do not delete code needed for that. Modify or drop that PL that would delete that code." The path stays, with all of its code: `docs/worker.md`, `docket delegable`, the `not-delegable:` field and the delegated review in `verify.py`. This item is narrowed to one change. Text that describes delegation as handing work "to a cheaper model" is reworded to describe the API runner, because no worker runs a cheaper model since `PL-2D28`. Narrowed rather than dropped because that text is now false: it says the runner exists to save on the model, when it runs the same model on the API credit. The places, from `grep -rn "cheaper model"` on 2026-10-19:
- `subprojects/docket/README.md` lines 39, 2590 and 3924
- the `delegable` help text in `subprojects/docket/src/docket/cli.py`
- `Item.delegability`'s docstring in `model.py`
- two output strings in `render.py`
- a comment and a mark in `plan.py`
- a check message in `checks.py`
- any test under `subprojects/docket/tests/` that pins one of those strings

`docs/worker.md` gains one sentence naming the API runner as its usual reader.

**Done when.** No text under `subprojects/docket/` says "cheaper model", `docs/worker.md` names `tools/headless_worker.py` as the API runner, and `bin/docket delegable` lists the same items before and after the change.

**Generator check.** Not a head and not a re-entry: a single decision that missed one consumer, `tools/headless_worker.py`, which landed the same day.
