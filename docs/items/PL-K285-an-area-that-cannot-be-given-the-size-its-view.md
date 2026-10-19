---
id: PL-K285
title: An Area that cannot be given the size its View needs says so rather than collapsing it, which is the second of the three properties docs/interface-provenance.md records Blender not supplying
priority: P1
effort: M
status: done
classes: safety, anticipated
feature: interface-areas
touches: src/anesthesia_sim/layout/, src/anesthesia_sim/app/, tests/unit, tests/integration, docs/ARCHITECTURE.md
blocked-by: PL-1FT6, PL-TH35
added: 2026-09-16
closed: 2026-10-19
pr: 1622
payoff: an Area too small for its View states the size it needs instead of clipping or collapsing the View, and a border drag stops at a neighbour's need
verify: uv run pytest tests/unit/test_layout_sizing.py tests/unit/test_view_registry.py tests/integration/test_layout_adapter.py && grep -q 'def settle' src/anesthesia_sim/layout/sizing.py && grep -q 'def too_small_text' src/anesthesia_sim/app/view_registry.py
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

**Measured with `PL-W9P6`, 2026-10-18.** Qt will not shrink a widget below its
minimum size, so the screen and the model can disagree. On the dashboard,
below a window about 1266 px wide, the accounting sidebar is held at its
minimum width while the model's 0.18 fraction would give it less. Nothing
collapses, but the model's fractions no longer describe the screen. This
item's answer to whether a minimum is a request or a constraint decides which
one gives way, and `app/area_layout.py`'s `_lay_out` is where it applies.


## Built 2026-10-19

**What `PL-30L5` Q2 changed.** Q1's clause that a split which cannot give
both halves their minimum is refused was replaced on 2026-10-11 (project
owner, ratified): a split is refused only below the structural minimum, the
header and one line of a notice, and a half too small for its View is allowed
and shows this item's statement. So nothing raises `LayoutRefused` for a
View's minimum. The model holds no minimum at all, and `layout/sizing.py`
decides it against an extent in pixels.

**Decided in the build, each the one clearly correct option.**

- *The minimum wins, and the neighbours give way.* An Area whose share would
  be less than its need is held at its need, and the other children of its
  split give up the room in proportion to their fractions. The stored
  fractions are not changed, so they apply again once the window is large
  enough. Changing them would make a window resize rewrite the reader's
  layout.
- *Who gives way when nothing fits.* The Areas that the latest change moved
  are held at their header first, and the ones it left in place only after
  them. So a split's new halves say they are too small, rather than taking
  the room from an Area the reader did not touch.
- *A View's need* is the larger, on each axis, of its registry entry's
  declared minimum and the least size Qt would hold its widget to, with the
  header and rule above it. The widget's own minimum grows with the number
  of runs (the concentration chart's minimum height is 558 px with one run
  and 601 with two, measured offscreen), so a declared constant alone would
  clip it.
- *The layout's minimum size hint is every need added up* (Q2, Q4). The
  dashboard's page is a `QScrollArea`, so it grows to that and scrolls,
  which it already did before this item: at 1366 by 900 px the page was
  1525 px tall. The statement therefore appears only where the host cannot
  grow. In this build that is no shipped window; the tests drive it in a
  window held at a fixed size.
- *The declared minimums are placeholders* (look and placement, project
  owner, 2026-10-18): concentration chart 420 by 300 px, wash-in 300 by 220,
  parameter controls 220 by 160, agent accounting 220 by 160. Each is the
  size at which the View is still legible empty; the widget's own minimum
  rules once it holds a run.
- *The notice's wording* is `PL-DB5G` Q3's, written in
  `app/view_registry.py`'s `too_small_title` and `too_small_text`. Its body
  is restated from the Area's size under its header whenever the Area is
  resized, and it shows no value from any run (Q4).

**The tests.** `tests/unit/test_layout_sizing.py` works every expected size
out by hand: the holding, the giving way, the order of letting go, a
too-small Area drawn again, and the shipped Induction Workspace at 508 by
408 px with no zero extent. `tests/integration/test_layout_adapter.py` § "an
Area too small for its View" drives the split, the chosen View, the drag
stop at a declared need, the notice restated as the Area grows, a layout
opened in a fixed window, a scrolling page that grows, and the minimum size
hint equal to the model's sum. The adapter's older tests now run at 800 px,
since a quarter of 400 px is narrower than an Area's header (177 px
offscreen).
