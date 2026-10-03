---
id: PL-Z64T
title: ROADMAP.md's v0.6.0 gate lists PL-5B1N and PL-TDBT under the product lane, while docket computes crossing and workflow for them, and nothing holds the three lane groups to the lane each entry's touches computes
status: untriaged
added: 2026-10-03
---

**Problem.** ROADMAP.md's v0.6.0 gate lists PL-5B1N and PL-TDBT under the product lane, while docket computes crossing and workflow for them, and nothing holds the three lane groups to the lane each entry's touches computes

**Evidence, 2026-10-03.** Recomputed with `Item.lane(config.workflow_paths)` (`subprojects/docket/src/docket/model.py`) for every open entry under `ROADMAP.md`'s three "Cleared before v0.6.0 begins" groups: 42 open entries, 2 in the wrong group. `PL-5B1N`, listed under the product lane at `ROADMAP.md:5545`, computes `crossing`, since its `touches` includes `tools/contrast_check.py`; `PL-TDBT`, listed under the product lane at `ROADMAP.md:5580`, computes `workflow`, its one `touches` entry being `docs/pr-bodies`. `ROADMAP.md:5386` to `:5390` says the groups follow the lane `docket.toml` computes from each item's `touches`, so the grouping is stale, and no check reads it. Found by the project's coordinator session while reviewing the gate.

**Why it matters.** The groups are how the gate is meant to be worked: the product and workflow lanes share no files, so they run concurrently in two sessions. An entry in the wrong group sends a session to work it beside one it shares a file with - `PL-5B1N` touches `tools/contrast_check.py`, a workflow path - and nothing says so.

**Not covered by.** `PL-M26Q` (`bin/docket gate` prints no lane split) and `PL-KRGY` (where `workflow_paths` places a path) are neighbours, not this. `PL-YBFB` would move `PL-5B1N` out of Gate 2 altogether, which removes one of the two rows and leaves the drift unchecked.
