---
id: PL-K285
title: An Area that cannot be given the size its View needs says so rather than collapsing it, which is the second of the three properties docs/interface-provenance.md records Blender not supplying
status: blocked
feature: interface-areas
added: 2026-09-16
priority: P2
effort: M
blocked-by: PL-1FT6, PL-TH35
classes: safety, anticipated
touches: src/anesthesia_sim/layout/, src/anesthesia_sim/app/, tests/unit
---

**Problem.** An Area that cannot be given the size its View needs says so rather than collapsing it, which is the second of the three properties docs/interface-provenance.md records Blender not supplying

**Why it matters.** The second of the three properties
`docs/interface-provenance.md` records Blender not supplying, and the one with
no precedent to copy. Blender's answer when a region will not fit is
`RGN_FLAG_TOO_SMALL` and collapse to zero extent, which for a 3D tool costs a
keystroke; here `docs/MODEL.md` requires that a required value is never hidden
to make room, and a silent collapse is exactly the failure that division exists
to prevent.

**Done when.** The View contract says whether a declared minimum is a request
or a constraint; a split or a border drag that cannot meet it is refused or
reported rather than satisfied by collapsing; the interface says so where a
conditional surface genuinely cannot fit; and a test drives an Area below the
size its View needs and asserts the stated behaviour rather than a zero-extent
pane.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 8.

---

## Design round 2026-09-27: recommendations

Recommendations, not decisions: the thread that records the project owner's
answer marks each `(project owner, DATE, ratified)` or replaces it. One is
learner-visible and the owner's: whether `set_view` into a too-small Area is
allowed.

**Q1. Request or constraint?** **Recommendation: a constraint**, declared
per kind on the registry entry in logical pixels (width, height), with a
small floor for an empty Area. The model enforces it: `split(area, ...)` that
cannot give both halves their minimum raises `LayoutRefused(area, needed,
available)`, and `resize`/a border drag is clamped at the chain's minimum,
never past it. The adapter mirrors each minimum onto the widget with
`setMinimumSize` and sets `childrenCollapsible(False)` on every `QSplitter`,
so Qt's own range computation (`getRange` / `closestLegalPosition` in
`src/widgets/widgets/qsplitter.cpp`, qt/qtbase, read 2026-09-27) stops a drag
before the model is asked, and the two agree by construction. A refused split
appears as an unavailable menu entry that states the reason (`PL-M352`).
*Request* was refused because a request the container may decline is the
warning-after-the-fact shape the expert-review rule steers away from.

**Q2. What happens when a live window cannot honour it.** Qt propagates the
splitter minima into the window's `minimumSizeHint`, so a window cannot be
dragged below the sum of its Areas' minima. The case that remains is a
Workspace **opened on a smaller screen** (a saved file on another machine, a
monitor change, `PL-HJPY`'s fractions make this ordinary rather than rare).
**Recommendation:** at load the model computes `too_small(available) ->
[AreaId]` against the screen's available geometry, and each such Area draws
the **too-small state**: the header still names the View, and the content is
replaced by a statement of the size needed against the size available.
Nothing is scaled, clipped or collapsed. Measured at the source: when a
`QSplitter` is smaller than the sum of its children's minima, `qGeomCalc`
sizes children *below* their minimums and the widgets clip silently, which is
exactly the plausible-wrong-layout failure this item refuses. Refusing to load
the Workspace was considered and refused: it would discard the reader's
layout for a screen they may plug back in tomorrow.

**Q3. `set_view` into a too-small Area.** **Recommendation (learner-visible):
allowed, and the Area shows the too-small state.** Refusing would hide the
route to fixing it: the reader sees the stated size, drags the border, and
the View appears. *Alternative:* refuse with a reason; a defensible choice,
recorded for the owner.

**Q4. What the test asserts.** A headless test drives an Area below its
kind's minimum through `resize` and asserts the clamp; a second calls `split`
on an Area that cannot fit two and asserts `LayoutRefused` with the numbers;
a third loads a fixture Workspace against a small `available` and asserts
`too_small` names the Areas and nothing has zero extent. The Qt-side test
asserts `minimumSizeHint` of the built window equals the model's sum. The
appearance of the state is entry 20's (`PL-M3X6`).

## Answers 2026-09-27

**Every recommendation above: ratified** (project owner, 2026-09-27,
ratified, over the alternative each names). The one decision the owner
specified otherwise is `PL-WV9K` Q4: layouts are saved by an explicit "Save
as default" action in the layout menu, not automatically; `PL-WV9K`
§ "Answers 2026-09-27" carries that design.
