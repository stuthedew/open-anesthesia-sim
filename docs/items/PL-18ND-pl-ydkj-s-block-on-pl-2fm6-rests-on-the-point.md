---
id: PL-18ND
title: PL-YDKJ's block on PL-2FM6 rests on the point-movement rate being its main input, which the PL-YSZN measurement contradicts for the cost that now dominates
status: untriaged
added: 2026-09-08
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

**Why this is a separate item rather than an edit.**
`origin/claude/m4-implementation-status-be2syh` is holding `PL-YDKJ`'s file
with the edit that created the block, so a second edit collides at merge. The
finding is recorded here and in `docs/WORKING_NOTES.md` under "Measured and
answered: a server-rendered chart is not the way out", which carries the whole
measurement.

**Not an argument to unblock it.** The ordering may still be right: `PL-2FM6`
changes what the chart draws from, which changes the *point count* as well as
the movement rate, and that is the input the walk does care about. The defect
is that the block's stated reason names the quantity that stopped mattering.
Re-check the reason against `PL-YSZN`, and either restate it or drop the edge.

**First step.** After `origin/claude/m4-implementation-status-be2syh` merges,
read `PL-YDKJ`'s block paragraph against `PL-YSZN`'s walk measurement and
correct the reason it gives.
