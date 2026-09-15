---
id: PL-WBLM
title: PATH_SUFFIXES carries no image suffix, so a cited .png or .svg is never resolved and docs/worker.md's out/dashboard.png is unchecked
status: untriaged
added: 2026-09-15
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
