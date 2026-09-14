---
id: PL-8KPD
title: Drop PL-0QLX as a duplicate of PL-Y6W9 once claude/pensive-haslett-0f5025 lands: both capture the hook tests red under macOS's system python3, and PL-Y6W9 is the one worked
status: untriaged
added: 2026-09-14
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
