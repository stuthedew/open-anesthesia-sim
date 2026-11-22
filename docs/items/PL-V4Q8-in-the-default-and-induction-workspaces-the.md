---
id: PL-V4Q8
title: In the Default and Induction Workspaces the four parameter dials are 43 to 85 px long at every window size, because their four cards share one row at their least width while the Parameters Area has spare room
status: untriaged
feature: interface-design-review
added: 2026-11-22
---

**Problem.** In the Default and Induction Workspaces the four parameter dials are 43 to 85 px long at every window size, because their four cards share one row at their least width while the Parameters Area has spare room

**Go-ahead.** The design review that found this was approved by the project owner (project owner, 2026-11-22). It ran offscreen on `a7eb53f`, with screenshots of each Workspace and each View at 1366 by 768 and 1920 by 1080 in `/mnt/project-files/v0.7.0/design-review/`.

**What was measured.** Offscreen, the dials for fresh gas flow, delivered
agent, alveolar ventilation and cardiac output are 51, 85, 54 and 43 px long
in Default and Induction at both 1366 by 768 and 1920 by 1080. In Maintenance,
where the Area is wider, they are 83 to 99 px at 1366 and 138 to 154 px at
1920. At 1920 by 1080 the Default Parameters Area is about 590 px wide.

**Why it matters.** A 43 px dial spread over its whole supported range moves
several steps per pixel, so a mouse cannot set a value precisely. The arrow
keys still can, but most learners drag.

**What to do.** Let the cards grow to fill the Area's width, or lay them out
two by two where the Area is narrow, so each dial gets at least a set length.
The arrangement is a placeholder the session decides.

**Done when.** A test opens each shipped Workspace at 1366 by 768 and finds
every dial at least the set length.
