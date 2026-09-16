---
id: PL-WBLM
title: PATH_SUFFIXES carries no image suffix, so a cited .png or .svg is never resolved and docs/worker.md's out/dashboard.png is unchecked
status: dropped
feature: dev-tooling
touches: tools/doc_check.py
added: 2026-09-15
closed: 2026-09-16
reason: The check would fire on nothing. `PATH_SUFFIXES` is indeed missing `.png` and `.svg`, but the only image citation in the tree is `docs/worker.md:40`'s `out/dashboard.png`, which names a *generated* file that `PL-MXSL` may exempt anyway - there is no tracked image asset for a widened check to resolve. `CLAUDE.md`'s "a check earns its place every run, or it is retired" decides it: adding a suffix before anything exists for it to match buys a check that costs attention forever and changes no decision, which is the shape that trains a session to skim the output where a real advisory also appears. The item's own brief reaches the same conclusion - "a note to revisit when the first tracked image lands, not work now". Dropped rather than left open so the queue stops offering work nobody should start; the finding survives here, and recapture is correct the day a tracked `.png` or `.svg` lands, at which point the argument reverses
---

**Problem.** PATH_SUFFIXES carries no image suffix, so a cited .png or .svg is never resolved and docs/worker.md's out/dashboard.png is unchecked

**Where.** `tools/doc_check.py`, `PATH_SUFFIXES` - `.py`, `.json`, `.md`,
`.yml`, `.yaml`, `.toml`, `.sh`, `.cfg`, `.ini`, `.lock`, `.txt` and nothing
else. A code span whose suffix is not in that set is read as prose rather than
as a claim about a file, so `` `out/dashboard.png` `` at `docs/worker.md:40` is
not resolved and never has been.

**Found 2026-09-15** while measuring for `PL-MXSL` (the `.gitignore` exemption
for cited directories), whose brief names this as one of the two accidental
escapes that made the `out/` workaround possible.

**Whether it is a gap depends on whether this repository will carry images**,
which is the part to decide rather than assume. Today the only image citation
names a generated file, which `PL-MXSL` may exempt anyway; adding `.png` and
`.svg` before there is a tracked asset would mean a check that fires on nothing
- which `CLAUDE.md`'s "a check earns its place every run" argues against. So
this is a note to revisit when the first tracked image lands, not work now.

**Why it matters.** It matters as a recorded decision rather than as work, and
the reasoning is in this item's `reason` field. In short: the escape is real -
a code span whose suffix is outside `PATH_SUFFIXES` is read as prose rather
than as a claim about a file - but it has nothing to escape with. The sole
image citation in the tree names a generated file, so widening the suffix list
today buys a check with no instance to catch, and `CLAUDE.md` is explicit that
such a check is a defect in the check rather than coverage.

**Done when.** Nothing, deliberately: dropped 2026-09-16, with the `reason`
field recording why so the finding is not re-raised from scratch. `PL-MXSL`
carries the `out/` question this was found beside; recapture is correct the day
a tracked `.png` or `.svg` lands in the repository.
