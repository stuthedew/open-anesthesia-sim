---
id: PL-R1WQ
title: Nothing says where the view registry lives, how a view-kind tag is allocated so a class rename does not trip the loud failure meant for a missing view, or how a pure-Python LayoutModel validates a kind tag without importing a Qt view
priority: P2
effort: M
status: blocked
classes: planning
feature: interface-areas
blocked-by: PL-1FT6
touches: docs/ARCHITECTURE.md
added: 2026-09-16
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
