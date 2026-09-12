---
id: PL-7SVX
title: Delete spikes/ and the last Flet import once the port is complete
priority: P2
effort: S
status: ready
classes: refactor, infra
feature: qt-port
touches: spikes, tools/import_boundary_check.py, src/anesthesia_sim/app
added: 2026-09-10
verify: uv run python tools/import_boundary_check.py && ! grep -rq 'import flet' src/anesthesia_sim/
---

**Problem.** Delete spikes/ and the last Flet import once the port is complete

**`v0.5.1`'s Required scope, item 7, and it is the last one.**

Two deletions: `spikes/` entire - `PL-55DH` built it to throw away cleanly, and
`rm -rf spikes/` is the whole procedure - and the last `import flet`.

**It is also the check that the port is actually finished.** While any module
imports Flet, both toolkits are in the tree and the release has not crossed the
boundary it claims to. `tools/import_boundary_check.py` is where that becomes a
rule rather than a sweep: a boundary declaring that *nothing* imports Flet is
the same shape as the two it already enforces, and it is what stops the next
change reaching for the old toolkit.

**Do not run this early.** The spike is the working reference every other item
in this milestone reads from, so it goes last.

**Why it matters.** It is the check that the port actually finished, not a
tidy-up after it. While any module imports Flet both toolkits are in the tree,
the dependency declaration cannot be narrowed, and the release has not crossed
the boundary it claims to. Making it a rule rather than a sweep is what stops
the next change reaching for the old toolkit:
`tools/import_boundary_check.py` already enforces two boundaries of exactly this
shape, and "nothing imports Flet" is a third.

**Done when.** `spikes/` is deleted, no module under `src/anesthesia_sim/`
imports Flet, and `tools/import_boundary_check.py` declares and enforces that as
a boundary so the absence is held rather than merely current.

**Do not run this early.** The spike is the working reference every other item
in this milestone reads from, so it goes last.
