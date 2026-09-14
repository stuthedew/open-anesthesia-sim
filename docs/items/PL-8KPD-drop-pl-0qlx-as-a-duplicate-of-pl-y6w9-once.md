---
id: PL-8KPD
title: Drop PL-0QLX as a duplicate of PL-Y6W9 once claude/pensive-haslett-0f5025 lands: both capture the hook tests red under macOS's system python3, and PL-Y6W9 is the one worked
priority: P3
effort: S
status: done
classes: docs
feature: queue-hygiene
touches: docs/items/
added: 2026-09-14
closed: 2026-09-14
verify: grep -q '^status: dropped' docs/items/PL-0QLX-*.md && grep -q '^reason: duplicate of PL-Y6W9' docs/items/PL-0QLX-*.md
---

**Problem.** Drop PL-0QLX as a duplicate of PL-Y6W9 once claude/pensive-haslett-0f5025 lands: both capture the hook tests red under macOS's system python3, and PL-Y6W9 is the one worked

**Found 2026-09-14** by `bin/docket stranded` at the start of `PL-Y6W9`'s
session: `PL-Y6W9` was captured on `claude/trusting-cerf-468dc8` (pull
request 581) and `PL-0QLX` on `claude/pensive-haslett-0f5025` eight minutes
apart, for the same eight red tests. `PL-Y6W9` carries the fuller brief and
is the one the project owner named, so it was recovered and worked; the other
branch's file was left alone because that session was live, and a second edit
to it would have collided at merge.

**Done when.** `PL-0QLX` is `status: dropped` with a reason naming
`PL-Y6W9`, on the default branch. Its file is not deleted.

**Done 2026-09-14** (project owner's instruction, in the session that cut
v0.4.25). `claude/pensive-haslett-0f5025` had landed - `PL-0QLX` is on
`origin/main` - so the condition this item waited on was met, and `PL-0QLX` is
`dropped` with a reason naming `PL-Y6W9` and #584, where that item is worked.
This file was recovered from `origin/claude/nifty-gauss-rgoya2` (#584's
branch), where it was captured; #584 still carries the untriaged copy, so
whichever of the two merges second resolves an add/add on this one file by
keeping the `done` version - the same shape #584 already resolved for
`PL-Y6W9` against #581.
