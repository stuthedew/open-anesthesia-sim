---
id: PL-W9P6
title: Build the one adapter module that drives the Qt widget tree from the LayoutModel, and turn the Qt port's inert splitter handles live
status: blocked
feature: interface-areas
added: 2026-09-16
priority: P2
effort: M
blocked-by: PL-1FT6
classes: feature
touches: src/anesthesia_sim/app/, src/anesthesia_sim/layout/, tests/integration
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
