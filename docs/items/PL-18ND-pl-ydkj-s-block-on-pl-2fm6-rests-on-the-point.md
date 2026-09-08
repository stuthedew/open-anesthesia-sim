---
id: PL-18ND
title: PL-YDKJ's block on PL-2FM6 rests on the point-movement rate being its main input, which the PL-YSZN measurement contradicts for the cost that now dominates
priority: P3
effort: S
status: done
classes: docs
feature: teachable-case
milestone: v0.4.11
touches: docs/items/PL-YDKJ-decide-whether-the-chart-should-keep-patching.md
added: 2026-09-08
closed: 2026-09-08
verify: python3 tools/doc_check.py check && grep -q 'Decided: option 1' docs/items/PL-YDKJ-decide-whether-the-chart-should-keep-patching.md
---

**Problem.** PL-YDKJ's block on PL-2FM6 rests on the point-movement rate being its main input, which the PL-YSZN measurement contradicts for the cost that now dominates

**Where the block came from.** `PL-YXXG` moved `PL-YDKJ` from
`needs-decision` to `blocked-by: PL-2FM6` on 2026-09-08, reasoning that
`PL-2FM6`'s brief "asks for exactly this ordering - the point-movement rate is
its main input, and this item changes it" and that deciding now "would size the
chart against a movement rate that is about to change."

**What the measurement says.** `PL-YSZN`, the same day: `page.update()` on a
saturated chart where *nothing had changed since the last one* costs what a
full frame costs, and both are linear in the number of point controls at about
24.5 us each. Flet's diff walks the tree whether or not anything moved, so the
Python-side cost that dominates today is a function of how many points are
drawn and not of how many of them move.

**So the premise is half true, and the half it is true of is no longer the
binding cost.** The movement rate *was* the main input while the client was the
bottleneck - `PL-Q197` measured ~17 900 operations a second saturating the
Flutter side, and the operation count is exactly what a movement rate produces.
It is not the input to the walk. Whether `PL-2FM6` should still gate `PL-YDKJ`
therefore turns on which of the two costs the sizing decision is about, and the
block was written as though only one existed.

**Why this was filed separately rather than edited in.** When the finding was
made, `origin/claude/m4-implementation-status-be2syh` was holding `PL-YDKJ`'s
file with the edit that created the block, so a second edit would have collided
at merge. That branch has since merged (`#473`), so the collision is
historical. The measurement itself is in `docs/WORKING_NOTES.md` under
"Measured and answered: a server-rendered chart is not the way out".

**This item is not blocked, and nothing here is waiting on `PL-2FM6`.**
`PL-2FM6` is what `PL-YDKJ` is blocked on; it is named above only because the
sentence under review is about that edge. Correcting a reason is reading two
paragraphs against one measurement, and both are on `origin/main` now.

**Nor is it an argument to drop the edge.** The ordering may well be right for
a reason the block does not give: `PL-2FM6` changes what the chart draws from,
so it changes the *point count* as well as the movement rate, and the point
count is the input the walk does care about. The defect is that the stated
reason names the quantity that stopped mattering, which will read as settled to
every session that meets it.

**First step.** Read `PL-YDKJ`'s block paragraph against `PL-YSZN`'s walk
measurement, and either restate the reason in terms of the point count or drop
the edge and return the item to `needs-decision`.

**Resolved by the second of the two dispositions this item named** (project
owner, 2026-09-08): the edge is dropped rather than the reason restated,
because `PL-YDKJ` was decided outright. Option 1 is stable under `PL-2FM6` -
what `PL-2FM6` changes is where the drawn points come from, not how many
controls the chart holds, and the column budget still decides that - so there
was no answer left for it to change. `PL-YDKJ` records the reasoning and the
measurements.
