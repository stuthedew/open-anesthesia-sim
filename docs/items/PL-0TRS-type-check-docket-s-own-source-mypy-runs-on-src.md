---
id: PL-0TRS
title: Type-check docket's own source: mypy runs on src only, so subprojects/docket/src is unchecked by make check and CI
status: done
milestone: v0.2.8
added: 2026-08-30
closed: 2026-08-31
commit: 685cbd5
pr: 102
---

**Problem.** `make check` and CI both run `uv run mypy src`, which is the
simulator's package only. `subprojects/docket/src/` has full annotations and a
`from __future__ import annotations` in every module, but nothing runs a type
checker over it. There is a standing error in it right now
(`roadmap.py:663`, a `MilestoneSection | None` assigned to a
`MilestoneSection`) that has never been reported by any gate.

**Why it matters.** docket is what every session reads the queue through, and
an unchecked type error in it fails at the moment a session is trying to find
out what to work on. The annotations are already there; only the gate is
missing.

**Where.** `Makefile`'s `check` target and `.github/workflows/`.

**Closed 2026-08-31 by PL-020's work**, not on its own branch. PL-020 (widen
the type-check gate past `src`, ship a `py.typed` marker) had already recorded
the same finding as a measured decision, and its gate covers
`subprojects/docket/src`, so this item's whole "Done when" is satisfied by
that change: `[tool.mypy] files` names the path, `Makefile` and
`.github/workflows/quality.yml` both run it, and the `roadmap.py` error is
fixed by declaring `milestone: MilestoneSection | None` rather than by a
suppression. The line number here reads 663 because the file has grown since;
the error was at 761 when it was fixed.

**Done when.** `make check` type-checks `subprojects/docket/src` as well as
`src`, CI does the same, and the existing `roadmap.py` error is fixed rather
than suppressed.
