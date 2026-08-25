---
id: PL-41YP
title: Assert every required displayed output reaches the rendered view
status: untriaged
feature: dev-tooling
touches: tests/
added: 2026-08-25
---

**Problem.** PL-036 makes `docs/MODEL.md`'s "Minimum displayed outputs" name
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
