---
id: PL-4JCC
title: The shipped Workspaces give the Parameters View an Area far taller than its content: 590 by 665 px in Default and 590 by 1083 px in Induction for about 90 px of controls (measured offscreen at 1920 by 1080, 2026-11-11), while no shipped Workspace but Maintenance shows a third View
priority: P3
effort: S
status: blocked
classes: ux
feature: window-is-the-frame
touches: src/anesthesia_sim/data/workspaces/default.json, src/anesthesia_sim/data/workspaces/induction.json
blocked-by: PL-CBYS
added: 2026-11-11
---

**Problem.** The shipped Workspaces give the Parameters View an Area far taller than its content: 590 by 665 px in Default and 590 by 1083 px in Induction for about 90 px of controls (measured offscreen at 1920 by 1080, 2026-11-11), while no shipped Workspace but Maintenance shows a third View

**Triaged, 2026-11-11: waits for `PL-CBYS`.** Since `PL-9YPR`, the column
that held Parameters alone is shared with Bookmarks and Branch in Default and
Induction, so the Parameters Area is about a third of the height it was.
`PL-CBYS` then changes every Area's height again. Measure once that has
landed, and close this item if the Area is no longer far taller than its
controls. Where the Views sit is a placeholder that the session decides.

**Why it matters.** Empty panel beside a chart is room the chart could use.

**Generator check.** A one-off: a placement chosen before a third View
existed to share the column.
