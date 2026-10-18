---
id: PL-W9P6
title: Build the one adapter module that drives the Qt widget tree from the LayoutModel, and turn the Qt port's inert splitter handles live
priority: P2
effort: M
status: done
classes: feature
feature: interface-areas
touches: src/anesthesia_sim/app/, src/anesthesia_sim/layout/, tests/integration, tests/unit/test_layout_model.py, tests/unit/test_import_boundary_check.py, tools/import_boundary_check.py, tools/contrast_check.py, docs/ARCHITECTURE.md, docs/interface-provenance.md, .claude/rules/ui-color.md, docs/items/PL-05M4-the-inert-splitter-handles-keep-the-host-s.md, docs/items/PL-2KXB-build-the-docking-affordances-a-reader-uses.md, docs/items/PL-K285-an-area-that-cannot-be-given-the-size-its-view.md, docs/items/PL-R1WQ-nothing-says-where-the-view-registry-lives-how.md, docs/items/PL-TH35-define-the-common-view-contract-every-app-view.md, docs/items/PL-ZBBP-retire-or-re-scope-claude-rules-ui-areas-md-and.md, docs/items/PL-RTG9-readme-carries-no-attribution-line-for-the.md, docs/items/PL-904Y-split-the-whole-interface-visibility-predicate.md, docs/items/PL-9LNF-three-app-surfaces-own-state-a-layout-could.md
blocked-by: PL-NWTM, PL-5HSG
added: 2026-09-16
closed: 2026-10-18
pr: 1592
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
Area without failing at construction. `PL-5HSG` closed the same day, as
the section above records.

## Built 2026-10-18

**What was built.** `app/area_layout.py` holds `AreaLayout`, which is built
from a `LayoutModel` and a `view_for` function that returns the widget for
each Area. It makes one `QSplitter` per `Split` and puts each Area's widget in
its place. It is the only module under `src/` that imports `QSplitter` or
`QSplitterHandle`, and `tools/import_boundary_check.py` now refuses either
import anywhere else (`PL-L8RN`, closed with this item). `inert_splitter` and
`freeze_splitter_handles` are deleted from `app/qt_widgets.py`.

**How a drag reaches the model.** Qt reports a drag on one handle. The adapter
converts the handle's pixel position into a fraction of the window, using the
new `LayoutModel.span(handle)` for where that handle's split begins and ends,
and calls `LayoutModel.resize`. It then sets every splitter's sizes from the
new model. So the whole line of joined borders moves, and no other border does
(`PL-5HSG`'s rule). A drag the model refuses with `LayoutRefused` leaves the
model unchanged and puts every splitter back. `layout_changed` is emitted once
per change. A window resize keeps the fractions and does not change the model.

**Decisions taken here, each a session's.**

- The setting sections moved out of the splitter into a plain column between
  the unconditional region and the Areas. Their heights are fixed by their
  contents, which a fraction cannot express, and keeping them out of an Area
  also keeps them out of anything closeable. Spare height still goes to the
  plots.
- The dashboard's layout is a module constant in `app/simulation_view.py`:
  one row, the chart Area at 0.82 and the accounting sidebar at 0.18, tagged
  `concentration_chart` and `agent_accounting`. The fractions give a sidebar of
  about 236 px at a 1366 px window, close to the old fixed 228 px. The tags and
  fractions are placeholders until `PL-R1WQ`'s registry and the shipped
  Workspaces replace them.
- The handle follows `PL-RQT1`: 8 px wide, drawing nothing at rest, the split
  cursor, and a 2 px `PRIMARY` line along every border on the hovered line.
  The width and line are look-and-feel placeholders for item 33's visual pass
  (#1589). `tools/contrast_check.py` now declares `PRIMARY` on `BACKGROUND` at
  3:1 for that line.
- The adapter draws one window and refuses a layout holding two, with a
  message saying that taking an Area into its own window is not built yet.

**Not here.** Minimum sizes: below a window about 1266 px wide, Qt holds the
sidebar at its minimum width while the model's fraction says less. That is
recorded on `PL-K285`. Shift, Escape, the `WARNING` line, corner drags, swap
and Workspace tabs are `PL-2KXB`'s.

**Regression test.** `test_the_border_between_two_areas_shows_the_page_rather_than_the_host`
in `tests/integration/test_dark_appearance.py` was run against `origin/main`
before this change, with `PYTHONPATH` set to a worktree of it. It failed on
`assert handle.isEnabled()`, because the inert handle was disabled. The
adapter's own tests need `AreaLayout`, which this change adds.

**Left for the thread working on `docs/MODEL.md` and `ROADMAP.md`.** The
coordinator gave those two files to another thread, so they were not edited
here. Three sentences are now stale:

- `docs/MODEL.md` § "Minimum displayed outputs", the paragraph beginning
  "Where the unconditional set lives in the build", says the region sits
  "above the splitter that every other surface sits in". The setting sections
  now sit in a plain column between the region and the Areas.
- `docs/MODEL.md` § "Color contrast, and the standard this interface is held
  to" says "the inert splitter handles keep the host's surface (`PL-05M4`)".
  The handles are live and enabled, and the gap shows `BACKGROUND`. This is
  the last thing `PL-05M4` waits on.
- `ROADMAP.md`'s paragraph on `anticipated` items says "the splitter handles
  are inert today" and cites `qt_widgets.py`'s `inert_splitter`, which is
  deleted.

