---
id: PL-7SVX
title: Delete spikes/ and the last Flet import once the port is complete
status: untriaged
feature: qt-port
added: 2026-09-10
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
