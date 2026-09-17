---
id: PL-1FT6
title: Build the LayoutModel: a pure-Python tree of Splits and Areas with split, join, resize, swap and set_view, a borders() collinear-chain query, and versioned JSON serialization over a root that holds one or more windows from v1
status: ready
feature: interface-areas
added: 2026-09-16
priority: P2
effort: L
classes: feature
touches: src/anesthesia_sim/layout/, tests/unit
verify: uv run pytest tests/unit/test_layout_model.py && grep -q 'def test_a_join_the_tree_cannot_express_is_refused' tests/unit/test_layout_model.py
---

**Problem.** Build the LayoutModel: a pure-Python tree of Splits and Areas with split, join, resize, swap and set_view, a borders() collinear-chain query, and versioned JSON serialization over a root that holds one or more windows from v1

**Why it matters.** This is the object every other piece of the area system
addresses. `PL-C842` decided it and nothing built it: `QSplitter.saveState()`
was disqualified as a source of truth because it records no Editor identity -
re-measured 2026-09-16 on PySide6 6.11.2, a three-pane splitter saves 35 bytes
that are byte-identical for the same three children in reverse order, and
`restoreState()` returns `True` restoring that state into a two-pane splitter.
A layout whose source of truth is an opaque widget blob cannot be tested,
reviewed in a diff, or made to fail loudly when it stops matching the
application.

**What it has to carry.** The root holds a *set of windows* from version 1 even
though v0.6.0 opens one, because a root that gains a window set later is a
schema migration against files a learner has already saved their own Workspaces
into (`PL-HJPY`). `borders()` returns the handles collinear with and adjacent to
a given one, which is how a splitter tree recovers Blender's aligned-border drag
without changing representation. A join the tree cannot express is **refused**,
never approximated: `PL-3J2P` took the tree knowing it is strictly less
expressive, on the stated ground that the limit shows up as an operation being
unavailable rather than as a wrong result.

**Done when.** `src/anesthesia_sim/layout/` holds a pure-Python model with no
Qt import, exercising split, join, resize, swap, `set_view`, `borders()` and a
versioned JSON round trip under test with no `QApplication`; a join the tree
cannot express raises rather than returning a different tree; and the serialized
root carries a window set at version 1.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 1.
