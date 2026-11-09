---
id: PL-L3JB
title: Cut v0.4.9 - the release where the checks were found to be checking less than they claimed
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
milestone: v0.4.10
touches: ROADMAP.md, pyproject.toml, uv.lock, docs/releases/v0.4.9.md, docs/items
added: 2026-09-07
closed: 2026-09-07
pr: 453
not-delegable: Proving a release cut means cutting the release; there is no command that can run beforehand and fail.
---

**Problem.** Cut v0.4.9 - the release where the checks were found to be checking less than they claimed

Fourteen items finished since v0.4.8 and nothing had shipped them. The cut
itself is `make release VERSION=0.4.9`; what it cannot generate is the prose
half - the version-table row, the `current baseline` mark, and the baseline
section saying what the release was *for* - which is the work recorded here.

**What it is for.** Every one of the fourteen is a guarantee that read as held
and was not being kept: a quality run red on `main` for three merges with
nothing surfacing it, an independence check a plain `import` walked past, an
accounting guard reading nothing from the object it judged, two tests
`docs/MODEL.md` requires and nobody wrote, a citation check that never opened
the queue and could not match a section title long enough to wrap, a `verify:`
able to re-enter `docket check` without bound, and a count labelled "open" that
excluded the untriaged items. That is the release's subject, and the baseline
section says so rather than listing the ids.

**No clinical value moves.** No equation, parameter, unit, numerical method or
solver step changed. The agent and reference-patient files did change, and only
in what they claim about their own numbers - `schema_version` 2, a `tier` and
`adopted` flag per source, a `provenance_gap` per file - with no stored value
moving. `git diff v0.4.8..HEAD -- src/anesthesia_sim/data/` shows no numeric
parameter altered, which is the check that statement rests on.

**Done when.** `pyproject.toml`, `uv.lock` and `docs/releases/v0.4.9.md` carry
the version, `ROADMAP.md` has the row, the moved baseline mark and the baseline
section, and `make check` passes. Tagging is the project owner's - a session
cannot push a tag (`PL-N936`).

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.9 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> No displayed value moves: no equation, parameter, unit, numerical method or solver step changed, and the agent and patient files gained provenance metadata - `schema_version` 2, a `tier` and `adopted` flag per source, and a `provenance_gap` naming what is unadopted - without one stored number moving. **What moved is how much of the apparatus was actually checking.** `main`'s quality run had failed on three consecutive merges with nothing surfacing it, because the whole-store `verify:` replay runs only on push to `main` (`PL-0ZGK`). The reference oracle's independence check walked only `ast.ImportFrom`, so a plain `import` went past the guard that makes that module evidence rather than a tautology (`PL-F5GN`). `require_valid_agent_accounting()` read nothing from the object it judged, so it would have accepted a result from another accounting period (`PL-X204`). Two tests `docs/MODEL.md` requires were documented and never implemented (`PL-GZP6`). The citation check quoted section titles as `[^"\n]+`, so any title long enough to wrap was unexamined rather than reported (`PL-X94L`), and it read neither the queue nor a single source docstring, which is where this project writes most of its citations (`PL-X2XX`); the two stale ones that found are fixed (`PL-8B1K`). A `verify:` command could re-enter `docket check` without bound (`PL-20CQ`), and a count labelled "open" excluded the untriaged items, understating the queue by exactly the number printed beside it (`PL-4WQS`). Source tier became machine-readable rather than prose (`PL-1JDD`), which immediately exposed a tier-2 source standing as the authority for `venous_pool_volume_l` and now says what it owes (`PL-FJGY`). v0.4.8's own tag had been pushed onto a commit where no release was cut (`PL-BKDP`).
