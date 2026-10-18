---
id: PL-JSY5
title: docs/MODEL.md's readout-row rung and its educational-disclaimer line both assume one window's width and one always-on-screen surface, which the area system makes false
priority: P1
effort: S
status: done
classes: docs, safety, anticipated
feature: interface-areas
touches: docs/MODEL.md
blocked-by: PL-NWTM
added: 2026-09-16
closed: 2026-10-18
pr: 1590
payoff: docs/MODEL.md says the readout row's rung follows the width of the unconditional region it sits in, not any Area, and where the use disclaimer lives and when it is in view, so neither statement is false once the layout is the reader's
verify: grep -q 'so its rung follows that region' docs/MODEL.md && grep -q 'Where the educational-use disclaimer lives' docs/MODEL.md
---

**Problem.** docs/MODEL.md's readout-row rung and its educational-disclaimer line both assume one window's width and one always-on-screen surface, which the area system makes false

**Why it matters.** Two statements in `docs/MODEL.md` assume the fixed layout.
§ "Displayed precision" records that the readout row "opens at whichever rung
the screen affords", sized from the *window's* width by
`WINDOW_SCREEN_FRACTION`; once the row sits in an Area the reader can drag, the
rung follows the Area rather than the window, and `PL-3355`'s reservation rule -
a value never wrapped away from its unit at any width the row is laid out at -
is what has to keep it honest at reader-chosen widths. And the colour section
describes the educational disclaimer as a line that is on screen *always*, which
is true only while one surface is permanent; the tier split makes the invariant
tier the natural home for it, and that has to be said rather than assumed.

**Done when.** Both statements say what is true once the layout is the
reader's: the rung follows the Area's width with the reservation rule named, and
the disclaimer's home is stated in § "Minimum displayed outputs" so the
"always" elsewhere stays true rather than being edited into vagueness.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 19.

## Re-confirmed 2026-10-18: changed shape, and built

**The brief's premise moved.** It expected the readout row to sit in an Area a
reader can drag. `PL-NWTM` put the row in the unconditional region instead,
outside the layout container, so no Area ever sizes it. The rung follows the
region's width: the window's width, divided between the runs' rows and the
control-change record (`PL-J8K2`). `docs/MODEL.md` § "Displayed precision" now
says so, names `PL-3355`'s reservation rule, and appends a dated measurement.
On the offscreen font, a 1366 px window with one run gives the row 1002 px,
3 px short of the 1005 px seven across needs, so it opens on four. That
undoes the outcome `PL-Z4K6` recorded. The region's division is `PL-W54S`'s,
and its brief carries the finding.

**The disclaimer's home was already decided.** `PL-J8K2` Q1 (project owner,
2026-10-11, ratified) put the use disclaimer in a line across the window's
foot, outside the layout container. `docs/MODEL.md` § "Minimum displayed
outputs" now states that home, says each top-level window carries the line
once break-out exists, and records the one gap: until the scrolling page goes,
the line sits below the visible part of a 700 to 1100 px high window. The
colour section's "always" now points there. A card asking the owner whether
the line must be always in view was withdrawn unanswered, because the v0.6.0
tiled layout puts it in view at no new cost and `PL-84QX`'s budget already
counts its row.
