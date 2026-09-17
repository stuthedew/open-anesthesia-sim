---
id: PL-0BSC
title: PL-WZBX's title says four entries sit under ROADMAP.md's 'Cleared by v0.5.0 itself', but only three of the eight are still open, so a reader sizing the correction from the title is off by one
priority: P3
effort: S
status: ready
classes: docs
feature: queue-hygiene
touches: docs/items
added: 2026-09-13
verify: bin/docket check && ! grep -q 'wave counts the four entries' docs/items/PL-WZBX-*.md
---

**Problem.** PL-WZBX's title says four entries sit under ROADMAP.md's 'Cleared by v0.5.0 itself', but only three of the eight are still open, so a reader sizing the correction from the title is off by one
**Why it matters.** `PL-WZBX` (the gate-counting defect that title describes)
is open at `ready`, so the next session to take it sizes the correction from
the title rather than from the store. Titles are what `bin/docket next`, the
session-start digest and the session list all print, so a wrong count in one is
read far more often than the body that would correct it - and this one is wrong
in the direction that sends a reader looking for an entry that has since
closed.

**Done when.** `PL-WZBX`'s title states the number of entries under
`ROADMAP.md`'s "Cleared by v0.5.0 itself" that are open when the fix is made,
read off `bin/docket wave` at that moment rather than from this brief; the file
is renamed with `git mv` to the slug the new title generates; and `bin/docket
check` raises no slug advisory for it.
