---
id: PL-VR27
title: "Cut the v0.4.5 release: going public, finished"
priority: P2
effort: S
status: done
classes: planning
feature: release-roadmap-seam
milestone: v0.4.6
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases/
added: 2026-09-06
closed: 2026-09-06
pr: 397
not-delegable: proving a release cut means cutting it; there is no command that can run beforehand and fail for the right reason
---

**What this was.** The v0.4.5 cut: `make release VERSION=0.4.5`, then the
prose half the tool deliberately leaves — the version-table row, moving the
`current baseline` mark off v0.4.4, and the baseline section and release
narrative that say what the release was *for*.

**Why 0.4.5 rather than 0.5.0.** `ROADMAP.md`'s "Versioning decision" picks the
number by the capability boundary a release crosses. This one crosses none:
`src/anesthesia_sim/data/` is byte-identical to v0.4.4 and every changed line
under `src/` is a comment or a docstring — the three changed modules are
AST-identical to v0.4.4 once docstrings are stripped. It stays inside the
`v0.4.x` patch track, and v0.5.0 remains the scoped milestone behind Gate 1.

**What it contains.** Eighteen items, one of which is the v0.4.4 cut itself
(`PL-XVCG`). The through-line is that v0.4.3 made this repository public
sideways — to stop Actions minutes being billed — and left the human-facing
pass unrun; v0.4.5 runs it, and finds a redistribution breach rather than a
gap. `PL-SHG5`, `PL-69K6`, `PL-N092`, `PL-4MHK`, `PL-YGF3`, `PL-HG5D` and
`PL-ZYDF` are that thread; `PL-NBWP` and `PL-NBCJ` are the prose that reached
`src/`.

**Where.** `pyproject.toml`, `uv.lock`, `docs/releases/v0.4.5.md`, and
`ROADMAP.md`'s version table, current-baseline section and release narrative.

**Done when.** The version is 0.4.5, the release notes exist, `ROADMAP.md`
carries the row and the baseline, and `make check` is green. The annotated tag
is the project owner's to push — a session cannot push a tag (`PL-N936`).
