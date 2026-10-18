---
id: PL-R1WQ
title: Nothing says where the view registry lives, how a view-kind tag is allocated so a class rename does not trip the loud failure meant for a missing view, or how a pure-Python LayoutModel validates a kind tag without importing a Qt view
priority: P2
effort: M
status: done
classes: planning
feature: interface-areas
touches: src/anesthesia_sim/app/, tests/integration, tests/unit, docs/ARCHITECTURE.md, docs/interface-provenance.md, tools/contrast_check.py, docs/items
added: 2026-09-16
closed: 2026-10-18
pr: 1599
payoff: an Area whose View kind this build does not know shows a failure in that Area rather than a wrong View, and renaming a class cannot change what a saved layout means
verify: grep -qr --include=view_registry.py 'ViewKind' src/anesthesia_sim/app
---

**Problem.** Nothing says where the view registry lives, how a view-kind tag is allocated so a class rename does not trip the loud failure meant for a missing view, or how a pure-Python LayoutModel validates a kind tag without importing a Qt view

**Why it matters.** `PL-C842` decided that "a view is registered by kind, never
a subclass" and that a saved workspace naming a view this build lacks must fail
loudly. Both halves rest on a tag whose allocation nobody has specified. If the
tag is derived from the class name or the display title, an ordinary rename
turns every saved workspace into the loud failure that was designed for a
genuinely missing view - so the safety mechanism fires on a refactor, which is
how a loud failure gets routed around and then ignored.

The second half is a boundary question: `PL-C842` puts the LayoutModel in pure
Python with one adapter importing Qt, so the model must validate a kind tag
without importing the view it names.

**Done when.** The registry's location, the tag's allocation rule and its
stability across renames are written down, and the LayoutModel's validation path
is stated in terms that do not require a Qt import.

## Area-model audit (PL-BNYF)

**Disposition: `missing-prereq`.** Surfaced 2026-09-16 by the area-model audit's completeness critic, after the main sweep had closed - which is the critic earning its place rather than a defect in the sweep.

---

## Design round 2026-09-27: recommendations

Recommendations, not decisions: the thread that records the project owner's
answer marks each `(project owner, DATE, ratified)` or replaces it.

**Q1. Where the registry lives.**
**Recommendation: one registry, on the Qt side, and no list of kinds in the
layout package at all.** A module under `app/` (proposed:
`app/view_registry.py`) holds a frozen mapping from tag to
`ViewKind(tag, title, factory, minimum_size, required_reachable)`. To the
layout package a View kind is an **opaque tag string**: the model checks its
syntax (lowercase snake case, `^[a-z][a-z0-9_]{0,39}$`), round-trips it
verbatim, and never asks what it names. The adapter (`PL-W9P6`) resolves each
Area's tag through the registry when it builds the widget tree; a miss draws
the failure state in **that Area** (Required scope entry 4; its appearance is
entry 20's), and the model keeps the tag unchanged, so a later save writes back
what was read: nothing substituted, nothing dropped. *Alternative refused:* a
pure-Python module in the layout package enumerating the shipped tags, checked
at startup against the Qt registry. It puts a list of the application's Views
inside the layout package - the coupling `docs/interface-provenance.md`
§ "Adopted" ("nothing in the layout layer knows a concrete view type exists")
and `PL-L8RN`'s boundary exist to prevent - and buys only an earlier failure for
a case the per-Area state already covers.

**Q2. How the pure model validates a tag without importing a Qt view.**
**Recommendation:** syntax in the model; membership as a query that takes the
known set as an argument, `LayoutModel.unknown_kinds(known)`, returning the
Areas whose tag is not in it. The adapter passes the registry's keys; a
headless test passes any set, which is how "a Workspace naming an unknown kind
loads with that Area marked" is asserted with no `QApplication`.

**Q3. How a tag is allocated so a rename does not trip the loud failure.**
**Recommendation:** a tag is a **string literal declared once, in the registry
entry beside the factory**, never derived from a class name, a module path or
a display title. Renaming a class or moving a module changes nothing a file can
see. Retiring or renaming a *tag* is a schema event, recorded in a
`RETIRED_TAGS` table in the same module - the old tag, the version it went,
and its successor tag where the View was renamed rather than removed - so a
saved Workspace naming it gets the specific message (renamed in that version,
or removed in it) and, where a successor exists, is offered the rename
explicitly rather than mapped silently. **A retired tag is never reused for a
different View.** Blender's precedent, verified at the source on 2026-09-27:
`eSpace_Type` in `source/blender/makesdna/DNA_space_enums.h` keeps
`SPACE_IMASEL`, `SPACE_SOUND`, `SPACE_SCRIPT`, `SPACE_TIME` and `SPACE_LOGIC`
as reserved numbers, with a comment that the order must not change and new
entries append at the end, so a file's id is never reinterpreted as another
editor.

**Q4. What pins it.** A unit test loads every shipped Workspace file
(`PL-KXTL`) and asserts each tag it names is registered, so a tag change that
forgets the shipped files fails in CI; a second asserts every registered kind
has a factory and that every tag in `REQUIRED_REACHABLE` (`PL-50PZ`) is
registered.

**What else the entry carries, decided elsewhere.** `minimum_size` per kind is
`PL-K285`'s; `required_reachable` is `PL-50PZ`'s; a View's own `state_version`
is `PL-TH35`'s and is independent of the file's `schema_version` (`PL-SSQW`),
so a change to one View never bumps the file.

## Answers 2026-09-27

**Every recommendation above: ratified** (project owner, 2026-09-27,
ratified, over the alternative each names). The one decision the owner
specified otherwise is `PL-WV9K` Q4: layouts are saved by an explicit "Save
as default" action in the layout menu, not automatically; `PL-WV9K`
§ "Answers 2026-09-27" carries that design.

## [superseded 2026-10-18] Blocked on `PL-W9P6`, 2026-10-12

Set by `PL-1FT6`'s close-out. Q2's half is built with no Qt import: `ViewKind`
checks the tag's syntax, and `LayoutModel.unknown_kinds(known)` returns the
Areas whose tag is not in the set a caller passes
(`src/anesthesia_sim/layout/tree.py`, `src/anesthesia_sim/layout/model.py`).
What is left is the registry module Q1 places in `app/` and the per-Area
failure Required scope entry 4 names. The adapter reads both when it resolves
a tag, so the registry is built with the adapter, its first consumer, rather
than ahead of it as a table nothing reads.

**`PL-W9P6` built, 2026-10-18.** The adapter exists without the registry.
`AreaLayout` takes a `view_for` function that returns the widget for each
Area, and `SimulationView._area_view` maps the dashboard's two tags to their
widgets and raises `LookupError` for any other tag. That function is the seam
this item's registry replaces. Q1's `app/view_registry.py` and the per-Area
failure state are still to build, so the work now reaches `app/` and the
integration tests as well as `docs/ARCHITECTURE.md`.

## Built 2026-10-18

`src/anesthesia_sim/app/view_registry.py` is Q1's registry, and
`AreaLayout` looks each Area's tag up in it. An unregistered tag draws an
`AreaNotice` in its own Area, `view_for` is never called for it, and the model
keeps the tag. Q3's tags are the four literals the shipped Workspaces and the
dashboard name, and `RETIRED_TAGS` is empty and checked at import: a retired
tag cannot be registered, and a successor must be. Q4's first test is
`test_every_shipped_workspace_names_only_registered_kinds` in
`tests/unit/test_view_registry.py`. The tests in
`tests/integration/test_layout_adapter.py` assert that a failed Area's visible
strings are the notice's two lines and nothing else (`PL-DB5G` Q4).

Choices made while building, inside the ratified design:

- **The entry is `RegisteredView`, not `ViewKind`.** `layout.tree.ViewKind`
  already names the tag's type, so Q1's `ViewKind(tag, ...)` entry took
  another name rather than shadowing it.
- **The entry has no `factory` yet.** Q1 lists one, and `PL-TH35` Q2 decides
  what it is called with: a `ViewContext` holding the run binding, the shared
  state and the saved state. A factory written before that context exists
  would take nothing a View could honestly be built from, since the
  dashboard's widgets are not yet constructible one per Area (`PL-9LNF`). So
  `AreaLayout` keeps the caller's `view_for` for a registered kind, and
  `PL-TH35` adds the field with its contract. Q4's second test, that every
  registered kind has a factory, arrives with the field. `minimum_size` and
  `required_reachable` stay `PL-K285`'s and `PL-50PZ`'s.
- **The titles are placeholders** ("Concentrations", "Wash-in",
  "Parameters", "Agent accounting"). Nothing shows them until the View
  chooser, Required scope entry 16, is built.
- **The notice leaves out `PL-DB5G` Q2's last line**, "Choose a View from the
  menu above", because no such menu exists yet. It says instead that the
  saved name is kept, so saving loses nothing. The chooser's item adds the
  line, and the explicit rename offer for a tag with a successor, when the
  menu exists. Placeholder wording.
- **The adapter takes `registered=` as a keyword**, defaulting to
  `REGISTERED`, so the adapter's tests draw a test-only kind without adding it
  to the shipped list.
