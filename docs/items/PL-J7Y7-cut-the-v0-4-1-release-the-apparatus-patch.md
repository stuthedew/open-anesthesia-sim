---
id: PL-J7Y7
title: Cut the v0.4.1 release: the apparatus patch
priority: P2
effort: S
status: done
classes: planning, docs
feature: planning-cadence
milestone: v0.4.2
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases/, docs/items/
added: 2026-09-05
closed: 2026-09-05
pr: 359
not-delegable: proving a release cut means cutting the release. No command
---

**Problem.** Eleven items have closed since v0.4.0 and nothing has stamped them
into a release. Filed before the work per CLAUDE.md's housekeeping rule: a
release cut carries no `PL-` id until somebody files one, so every in-flight
guard reads it as nobody's work — which is how two sessions cut v0.3.7
independently (`PL-66FP`). `PL-647D` is the precedent from the v0.4.0 cut.

**Why it matters.** The cut stamps `milestone: 0.4.1` so the next release does
not re-ship these eleven, and it is what lets `bin/docket release` cut again —
it refuses while the previous release is untagged.

**What is in it, checked rather than assumed.** A pure apparatus patch:
`src/`, `tests/` and `docs/MODEL.md` are **byte-identical to v0.4.0**, so no
equation, parameter, numerical method, unit or displayed value moved. What
changed is `.github/workflows/`, `CLAUDE.md`, `ROADMAP.md`, `docs/items/`,
`docs/resident-instructions.md`, `docs/consultant-brief.md` and
`subprojects/docket/`.

**Where.** `pyproject.toml`, `uv.lock`, `ROADMAP.md` (version-table row, the
`current baseline` mark, the baseline section), `docs/releases/v0.4.1.md`.

**Done when.** `pyproject.toml` reads 0.4.1, `uv.lock` agrees, the eleven items
carry `milestone: 0.4.1`, `docs/releases/v0.4.1.md` exists, `ROADMAP.md` carries
the row and the moved baseline, and `make check` passes.
