---
id: PL-DQD8
title: docs/MODEL.md's paragraph saying 'always' does not mean the disclaimer is in view on every screen today is stale since PL-NNML fixed the scrolling page, and it points to a gap the paragraphs above no longer state
priority: P2
effort: S
status: ready
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md, docs/INTERFACE.md
added: 2026-11-05
payoff: the specification says in one voice that the educational-use statement is always on screen
verify: ! grep -qF 'but it is not in view on' docs/INTERFACE.md
---

**Problem.** A paragraph in `docs/INTERFACE.md` § "What this list requires once the layout is the reader's" says that "always" does not mean the disclaimer is in view on every screen today. It has been stale since `PL-NNML` fixed the scrolling page, and it points to a gap that the paragraphs above it no longer state.

**Checked 2026-11-09:** The paragraph moved to § "Color contrast, and the
standard this interface is held to" (lines 7678 to 7682). It reads "*The
disclaimer line is always placed in the layout, but it is not in view on every
screen today* (`PL-JSY5`, 2026-10-18)", and says that the paragraphs in § "What
this list requires once the layout is the reader's" describe "the one gap in
that placement". Those paragraphs now say the reverse: "The disclaimer line and
the unconditional region are always in view" (`PL-NNML`, line 6592). They keep
the gap only as history, in the paragraph that opens "Before the region and the
line were fixed outside the scrolling part".

**Why it matters.** A reader of the colour argument is told that the
educational-use statement is sometimes off screen, and is sent to a gap the
other section no longer describes. The two sections disagree about whether
that statement is always visible, which is part of what keeps the simulator
from being mistaken for a monitor.

**Done when.** The paragraph says that the line has been in view at every
window height since `PL-NNML`, and points to the paragraph that says so. It may
instead be cut, since the colour argument needs only that the line is
permanent. The dated history stays where it is.

**Generator check.** One-off: a finding from the `docs/MODEL.md`
structure-read sweep of 2026-11-05.

**Present at the Gate 3 freeze (checked 2026-11-09).** The passage this item
fixes was already in its file at `817a4d88`, the commit that froze Gate 3, so
under ROADMAP.md § "The gate is a snapshot, not a moving target" the item
joins v0.7.0's frozen list rather than being deferred by its capture date.

**Done 2026-11-16.** The paragraph was rewritten rather than cut, as the
thread preferred. In `docs/INTERFACE.md` § "Color contrast, and the standard
this interface is held to", it now says that the disclaimer line has been in
view at every window height since `PL-NNML`, and points to the paragraph in
§ "What this list requires once the layout is the reader's" that opens "The
disclaimer line and the unconditional region are always in view". It keeps the
sentence that the colour argument needs only a permanent statement. The
sentence about "the one gap in that placement" is gone, because that section
no longer describes a gap. The dated history, the paragraph that opens
"Before the region and the line were fixed outside the scrolling part", is
unchanged. Docs sweep: both sections, and `grep -n 'in view'` over
`docs/INTERFACE.md` for other statements that the line is sometimes off screen.
The rewritten paragraph no longer cites `PL-JSY5` or its date, 2026-10-18.
Those recorded when the gap was found, and the gap is closed, so keeping them
on a sentence that now says the line is always in view would misattribute it.
`PL-JSY5` remains the record of the gap.
