---
id: PL-BYHS
title: ROADMAP.md says Flet is pre-1.0 and its 1.0 is excluded by an upper bound, but Flet is no longer a dependency
priority: P3
effort: S
status: ready
classes: docs
touches: ROADMAP.md
added: 2026-10-19
payoff: the roadmap's reason the version bounds will go stale names a dependency the project actually has
verify: ! grep -qF 'Flet is pre-1.0' ROADMAP.md
---

**Problem.** ROADMAP.md says Flet is pre-1.0 and its 1.0 is excluded by an upper bound, but Flet is no longer a dependency

**Why it matters.** `ROADMAP.md` gives Flet's pre-1.0 status as one reason the version constraints will go stale. Flet is no longer a dependency: `pyproject.toml` keeps it only in a comment explaining why it left, and `tools/import_boundary_check.py` refuses it under `src/`. A reader planning an upgrade would look for a bound that does not exist and miss the interface dependency that does.

**Done when.** The sentence names the interface dependency `pyproject.toml` declares today and how it is bounded, or drops the Flet clause.

**Checked 2026-10-24.** `ROADMAP.md` still says "Flet is pre-1.0 and its 1.0 is excluded by an upper bound", in the paragraph that begins "This is a multi-year project".
