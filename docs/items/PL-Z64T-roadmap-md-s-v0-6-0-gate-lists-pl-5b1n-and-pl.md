---
id: PL-Z64T
title: ROADMAP.md's v0.6.0 gate lists PL-5B1N and PL-TDBT under the product lane, while docket computes crossing and workflow for them, and nothing holds the three lane groups to the lane each entry's touches computes
priority: P3
effort: S
status: blocked
classes: defect
touches: ROADMAP.md, tools/doc_check.py, tests/unit/test_doc_check.py
blocked-by: PL-74T0
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-03 triage pass
added: 2026-10-03
---

**Problem.** ROADMAP.md's v0.6.0 gate lists PL-5B1N and PL-TDBT under the product lane, while docket computes crossing and workflow for them, and nothing holds the three lane groups to the lane each entry's touches computes

**Evidence, 2026-10-03.** Recomputed with `Item.lane(config.workflow_paths)` (`subprojects/docket/src/docket/model.py`) for every open entry under `ROADMAP.md`'s three "Cleared before v0.6.0 begins" groups: 42 open entries, 2 in the wrong group. `PL-5B1N`, listed under the product lane at `ROADMAP.md:5545`, computes `crossing`, since its `touches` includes `tools/contrast_check.py`; `PL-TDBT`, listed under the product lane at `ROADMAP.md:5580`, computes `workflow`, its one `touches` entry being `docs/pr-bodies`. `ROADMAP.md:5386` to `:5390` says the groups follow the lane `docket.toml` computes from each item's `touches`, so the grouping is stale, and no check reads it. Found by the project's coordinator session while reviewing the gate.

**Why it matters.** The groups are how the gate is meant to be worked: the product and workflow lanes share no files, so they run concurrently in two sessions. An entry in the wrong group sends a session to work it beside one it shares a file with - `PL-5B1N` touches `tools/contrast_check.py`, a workflow path - and nothing says so.

**Not covered by.** `PL-M26Q` (`bin/docket gate` prints no lane split) and `PL-KRGY` (where `workflow_paths` places a path) are neighbours, not this. `PL-YBFB` would move `PL-5B1N` out of Gate 2 altogether, which removes one of the two rows and leaves the drift unchecked.

**Re-measured 2026-10-03 at triage.** One of the two rows has moved: `PL-YBFB`
(#1309) put `PL-5B1N` among v0.6.0's deferrals to Gate 3, out of the lane
groups. `PL-TDBT` is still listed under "Cleared before v0.6.0 begins, the
product lane" (`ROADMAP.md:5694`), and its one `touches` entry,
`docs/pr-bodies`, is a `workflow_paths` entry in `docket.toml`.

**Generator check.** One of the five post-close instances of `PL-J6HP`'s fact
named in `PL-QWF8`'s check - here the lane groups restating what `Item.lane`
computes. `PL-74T0` records the head or refuses it as its cluster 2.

**Blocked on `PL-74T0`.** Whether the groups are held to `Item.lane` by a
check, or stop restating it now that `bin/docket gate` prints each lane
(`PL-M26Q`), turns on whether cluster 2's head makes a frozen gate's entries
one record, so a check built first could be work that head's fix removes.
Moving `PL-TDBT` to the workflow group is due either way and rides whichever
lands.
