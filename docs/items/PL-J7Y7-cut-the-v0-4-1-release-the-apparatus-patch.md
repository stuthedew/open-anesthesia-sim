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

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.1 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "The timeline" is `ROADMAP.md`'s.

> The fourth release to change nothing shipped, and it comes straight after the largest capability release the project has had, because cutting v0.4.0 walked the plan end to end for the first time in weeks and found it out of agreement with the tooling that reads it. `bin/docket wave` was classifying the [§ "The timeline"'s] `v0.4.1` row as a milestone - which freezes a debt gate - and that gate computed to **105 entries against Gate 0's 21**; the row is now `v0.4.x`, a patch track that freezes none, and the beat reads *scope v0.5.0* as the timeline always intended. The score architecture (`PL-T691`, `PL-2FM6` and three more) is placed in v0.5.0, where forking needs it and where `PL-011`'s dropped retention debt is actually paid. The advisory that catches an undeclared prose prerequisite was reading only the first id after a cue, so "blocked on A and on B" never checked B - it had a live instance in `PL-VZL0` and reported clean. Three contradictions inside the next release's own briefs are cleared, each of which would have stopped a worker on day one, including a two-item deadlock where `PL-GS5X` and `PL-X9KD` each waited on the other. Every CI job gained a `timeout-minutes` bound against a 360-minute default, superseded pull-request runs are cancelled for the runner slot rather than the now-free minute, and `CLAUDE.md` finally states when investing in the apparatus is correct rather than only warning against it. Eleven items. This is not the exact matrix exponential - that is the `v0.4.x` track's content and has not started.
