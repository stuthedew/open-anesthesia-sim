---
id: PL-T1X0
title: doc_check's _headings and _hash_headings read a # line inside a fence as a heading, and link anchors are checked against bold runs GitHub gives no anchor, so a shell comment in a fence answers a section citation and README.md#cite-this-repository passes; latent
status: untriaged
touches: tools/doc_check.py, tests/unit
added: 2026-10-04
---

**Problem.** doc_check's _headings and _hash_headings read a # line inside a fence as a heading, and link anchors are checked against bold runs GitHub gives no anchor, so a shell comment in a fence answers a section citation and README.md#cite-this-repository passes; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`_headings` (3933) and `_hash_headings` (3942) read lines inside a fenced block as titles, so `# make sure the venv exists` in a bash fence answers a `§ "make sure the venv exists"` citation. The link-anchor check (4052) tests anchors against `_headings`, which includes `**Bold.**` runs that GitHub renders without an anchor, so `[citing](../README.md#cite-this-repository)` passes. Not members of `PL-R417`. Latent: no citation or anchor rests on either today.
