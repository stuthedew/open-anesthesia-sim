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

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.5 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> v0.4.3 made the repository public to stop Actions minutes being billed rather than as a publication decision, and left the human-facing pass deliberately unrun; this release runs that pass and finds what the sideways route had left behind. Two publisher-copyright full texts — Baker & Farmery 2011 and Schüttler & Schwilden 2008 — were being redistributed from a public repository, against `docs/references/README.md`'s own statement that removing them was a prerequisite for going public. They came out on the day the breach was found, by a `git filter-repo` pass and a force-push rather than a delete commit, because both blobs were in the history from the commit that added them; GitHub Support ticket 4733783 covers the pre-rewrite commits still pinned by `refs/pull/*/head` refs the repository owner cannot reach. **The durable half is a check.** `make check` had passed on the broken state, because `doc_check` verifies the paths `docs/MODEL.md` cites and nothing verified that a file named in the reference index is present; it now refuses an entry naming a file the directory does not hold — the decidable half in code, with whether an entry *should* keep its file left to a person. **The rewrite's own costs are recorded rather than absorbed.** It stripped every commit signature, force-updated branch refs to a snapshot taken before the push and dropped two commits pushed into that window, and left four captures reachable on one branch only. Both losses were recovered, and `bin/docket stranded` learned to tell a rewritten history from an ordinary divergence. A branch deleted in this release's own cleanup held the last copy of two more items, recovered from the stale remote-tracking ref that `git fetch` does not prune — the case the no-prune guard exists to preserve. **And the front door exists.** `README.md` is written against the audience, boundary and status questions `PL-RM83` settled — two domain-literate readers, nothing whose truth is tied to a model version, capability rather than a version string — and retires the check that guarded the file's absence, together with both its invocations, in the same commit that writes it; `pyproject.toml` now describes the project and classifies its maturity, audience and subject. **The one thing that reached `src/` is prose.** `app/playback.py` had said that playing a run faster is "never a modelling one" without qualification: true for a run nobody touches, false for one in which a control moves, because the tick burst has no yield in it and the reachable simulated instants are therefore `multiplier × 0.1` s apart — 0.1 s at 1x and 30 s at 300x. Nothing arrives late and no displayed value is stale; what coarsens is which instants can be chosen, and pause-change-resume stays exact at every rate. `MAXIMUM_SIMULATION_STEP_S` stays 0.1 s on the same finding, argued rather than defaulted: 0.05 s would double the propagations per simulated second and buy tighter timing at 1x alone, since above it the interface's own grid dominates. Three files under `src/` changed and every changed line is a comment or a docstring — all three are AST-identical to v0.4.4 with docstrings stripped — and `src/anesthesia_sim/data/` is byte-identical, so no equation, parameter, numerical method, solver step or displayed value moved. Eighteen items, one of which is the v0.4.4 cut itself.
