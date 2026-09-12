---
id: PL-HQ03
title: ROADMAP item 24 names a core/controller default duplication that does not exist: controller.py holds two module-level assignments, both non-numeric, and its docstring disclaims holding defaults
priority: P2
effort: S
status: ready
classes: docs
feature: release-roadmap-seam
touches: ROADMAP.md
added: 2026-09-08
verify: python3 tools/doc_check.py check && grep -qF 'controller.py holds no numeric defaults' ROADMAP.md
---

**Problem.** ROADMAP item 24 names a core/controller default duplication that does not exist: controller.py holds two module-level assignments, both non-numeric, and its docstring disclaims holding defaults

**Why it matters.** A planned-milestone item that names work which does not
exist sends whoever scopes it looking for a duplication to remove, finds none,
and leaves them unsure whether they have misread the item or the tree has moved
under it. `controller.py` holds two module-level assignments, both non-numeric,
and its docstring explicitly disclaims holding defaults - so the tree is already
in the state item 24 asks for, and the item is a task that cannot be completed
because it is already done.

Cheap now, expensive later: it costs one paragraph today and a scoping session's
confusion whenever item 24 comes up.

**Done when.** `ROADMAP.md` item 24 either names a duplication that exists, or
records that the `core`/`controller` split it asked for is already in place and
what remains of its intent, if anything. Verified against `controller.py` rather
than from the item's own wording.
