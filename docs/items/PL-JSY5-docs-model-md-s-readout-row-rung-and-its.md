---
id: PL-JSY5
title: docs/MODEL.md's readout-row rung and its educational-disclaimer line both assume one window's width and one always-on-screen surface, which the area system makes false
priority: P1
effort: S
status: ready
classes: docs, safety, anticipated
feature: interface-areas
touches: docs/MODEL.md
blocked-by: PL-NWTM
added: 2026-09-16
payoff: docs/MODEL.md says the readout row's precision rung follows the width of the Area it sits in, and where the disclaimer lives, so neither statement turns false once a reader can resize the layout
verify: grep -q 'rung follows the width of the Area' docs/MODEL.md
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
