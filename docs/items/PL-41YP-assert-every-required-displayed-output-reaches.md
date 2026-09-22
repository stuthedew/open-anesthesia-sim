---
id: PL-41YP
title: Assert every required displayed output reaches the rendered view
priority: P2
effort: M
status: ready
classes: test
feature: dev-tooling
touches: tests/
added: 2026-08-25
---

> **Groomed 2026-09-22 (`PL-Y4YG`): still owed, and its premise has moved.**
> `PL-036` closed on 2026-09-22 binding § "Minimum displayed outputs" to a
> named test per bullet rather than to a `SimulationSnapshot` field (ratified
> over the field, because a field "proves the value still travels, never that
> a widget still draws it" - the comment above `BOUND_FAMILIES` in
> `tools/doc_check.py`). So **Problem**'s first sentence describes a design
> that was not adopted. The gap survives it: of the 33 tests the section
> names, 27 assert the toolkit-free frame or the model and 6 build a Qt
> widget, so the chain is now doc → named test → formatted value, and which
> bullets have no test reaching a drawn widget is the first thing to count.
> The harness **Notes** implied was missing exists: `tests/integration/`
> builds the real view offscreen (`PL-YCWZ`).
>
> Build it now. It is one test file with nothing downstream; switching its
> list to `PL-NWTM`'s declaration is a small change once that exists, and
> `PL-NWTM`'s own after-a-split-and-a-close test should extend this one rather
> than write a second. Naming the new test in each bullet lets the existing
> binding carry the widget link with no new check.

**Problem.** PL-036 makes `docs/MODEL.md` § "Minimum displayed outputs" name
the `SimulationSnapshot` field behind each bullet and checks those fields
exist. That proves the field exists, not that the interface displays it.

**Why it matters.** A snapshot field can exist with no widget behind it —
`circuit_time_constant_s` was exactly that for several releases. The doc →
field → widget chain has a second link, and a required output silently losing
its display is a presentation failure of the kind `CLAUDE.md` treats as
safety, not tidiness.

**Where.** `tests/`, against `app/simulation_view.py`.

**Notes.** This cannot live in `tools/doc_check.py`: reaching the widget needs
the application package, which that tool deliberately never imports so it can
run in a bare checkout. A test is the right home.

**Done when.** A test asserts each required displayed output reaches the
rendered view, and fails when one loses its widget.

**Confirmed 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
Unchanged: the test carrying the field-to-widget link is still what this item
is for. It reads `PL-NWTM`'s declaration once that exists, so the ordering
between the two is unaffected by the convention.
