---
id: PL-W9P6
title: Build the one adapter module that drives the Qt widget tree from the LayoutModel, and turn the Qt port's inert splitter handles live
priority: P2
effort: M
status: ready
classes: feature
feature: interface-areas
touches: src/anesthesia_sim/app/, src/anesthesia_sim/layout/, tests/integration
blocked-by: PL-NWTM, PL-5HSG
added: 2026-09-16
payoff: a reader can drag a border and the layout model changes with it, from one adapter module that is the only code in the app building splitters
verify: grep -q 'def test_a_drag_on_a_border_changes_the_layout_model' tests/integration/test_layout_adapter.py
---

**Problem.** Build the one adapter module that drives the Qt widget tree from the LayoutModel, and turn the Qt port's inert splitter handles live

**Why it matters.** `PL-C842` confined `QSplitter` to one adapter module so
that no View can see a splitter, call `saveState()`, or store its own
geometry - the property interchangeability rests on. The adapter is also where
v0.4.26's reservation is spent: `inert_splitter`
(`src/anesthesia_sim/app/qt_widgets.py`) disables every handle so that a
later item can turn them live, and this is that item.

**Done when.** One module builds and updates the Qt widget tree from the
`LayoutModel` and is the only place in the tree importing `QSplitter`; the
handles are live; `inert_splitter` is gone or reduced to what still wants inert
handles; and a reader can drag a border and see the layout model change rather
than the widget tree alone.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 2.

## [superseded 2026-10-18] Blocked on `PL-NWTM`, 2026-10-12

Set by `PL-1FT6`'s close-out. The model this item drives exists now. What
holds it is the readout section, still placed in the vertical splitter by
`SimulationView._restack_sections`: the adapter builds that splitter from the
model, and the model has no address for an unconditional value (`PL-NWTM`,
Required scope entry 7). Building today's dashboard from it would either make
the readouts an Area - the closeable placement `docs/MODEL.md` forbids - or
move them out, which is `PL-NWTM`'s work. A live handle on that splitter could
also drag the readouts to nothing, since a `QSplitter` child is collapsible by
default. `PL-R1WQ`'s registry is built with this item, its first consumer, and
`PL-TH35`'s contract after it.

## [superseded 2026-10-18] Blocked on `PL-5HSG` as well, 2026-10-12

[superseded 2026-10-18] `PL-5HSG` closed on 2026-10-18 in `#1579`, so a drag
already moves only the borders on its line when this item starts. The owner answered `PL-5HSG` on 2026-10-12 (ratified): a drag moves only the
borders on its line, as Blender's does, and that lands before this item. The
handles this item turns live give a reader their first drag, so a border they
did not touch must not move under it from the start.

**`PL-NWTM` done, 2026-10-18.** The unconditional values now sit in
`SimulationView.unconditional_region`, above the splitter, and
`SimulationView.layout_container` names the splitter tree this item builds
from the model. `_place_run` refuses a run whose region lacks a value that
`app/unconditional_set.py` declares, so the adapter cannot move one into an
Area without failing at construction. `PL-5HSG` still blocks this item.
